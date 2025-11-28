import re
import time
import json
from typing import List, Dict, Union, Optional
from tools.tool import Tool
from util.logs import Log

# The design allows usage of the OpenAI library.
# We wrap imports to ensure the code remains valid even if the library isn't present,
# though execution would fail.
try:
    from openai import OpenAI, APIError, RateLimitError, APIConnectionError
except ImportError:
    raise ImportError("The 'openai' library is required. Please install it via 'pip install openai'.")

# Note: This module uses the project's `Log` class for all logging.

# --- Custom Robustness Decorator ---
def exponential_backoff_retry(max_retries: int = 3, base_delay: float = 1.0):
    """
    A custom decorator to handle API reliability without external dependencies like 'tenacity'.
    Implements exponential backoff strategy: delay = base_delay * (2 ^ attempt).
    Handles standard OpenAI transient errors.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except (RateLimitError, APIConnectionError, APIError) as e:
                    # Attempt to find a Log instance on `self` (common case for methods)
                    local_log = None
                    if len(args) and hasattr(args[0], 'log'):
                        local_log = getattr(args[0], 'log')

                    # We catch errors that are likely transient.
                    # We do NOT catch AuthenticationError or invalid request errors.
                    if retries >= max_retries:
                        msg = f"Max retries ({max_retries}) reached. Raising error: {e}"
                        if local_log:
                            local_log.log(msg)
                        else:
                            print(msg)
                        raise e

                    delay = base_delay * (2 ** retries)
                    msg = f"API Error: {e}. Retrying in {delay} seconds..."
                    if local_log:
                        local_log.log(msg)
                    else:
                        print(msg)

                    time.sleep(delay)
                    retries += 1
                except Exception as e:
                    # Non-recoverable errors (e.g., Python runtime errors) raise immediately
                    raise e
        return wrapper
    return decorator

# --- The Agent Class Implementation ---
class Agent:
    """
    A robust, minimalist implementation of a ReACT agent.
    Leverages OpenAI API v1 and custom regex parsing for high reliability.
    """

    def __init__(self, system_prompt: str, tool_list: List[Tool], model: str, api_key: str, log: Log):
        """
        Constructor adhering to the design signature.
        
        Args:
            system_prompt: The base persona instructions.
            tool_list: List of Tool objects available to the agent.
            model: The OpenAI model ID (e.g., 'gpt-4o', 'gpt-3.5-turbo').
            api_key: The OpenAI API key.
        """
        # 1. Client Initialization
        # We instantiate the client here to validate the API key format immediately.
        self.client = OpenAI(api_key=api_key)
        self.model = model
        # Logging: use the provided Log instance
        self.log = log
        
        # 2. Tool Registry Construction
        # Convert list to dict for O(1) lookups during the execution loop.
        self.tools: Dict[str, Tool] = {tool.name: tool for tool in tool_list}
        
        # 3. System Prompt Engineering
        # We must augment the user's prompt with the tool definitions and formatting rules.
        self.system_prompt = self._construct_system_prompt(system_prompt)
        
        # 4. Regex Compilation
        # Pre-compile regex for performance and robustness.
        # This pattern captures the Action and Input across multiple lines.
        # It handles variable whitespace and ensures we capture the full input block.
        self.action_pattern = re.compile(
            r"Action\s*:\s*(.*?)\n+Action Input\s*:\s*(.*)", 
            re.DOTALL | re.IGNORECASE
        )

    def _construct_system_prompt(self, base_prompt: str) -> str:
        """
        Generates the full system prompt by injecting tool descriptions and formatting rules.
        This effectively programs the LLM's 'operating system'.
        """
        tool_desc_str = "\n".join([f"{t.name}: {t.description}" for t in self.tools.values()])
        tool_names = ", ".join(self.tools.keys())
        
        # The ReACT Template
        # Note the specific instructions on tokens "Action:" and "Action Input:"
        # and the "Observation:" stop sequence instruction.
        react_instructions = f"""
You are an intelligent agent capable of using tools to solve problems.
You have access to the following tools:

{tool_desc_str}

To use a tool, you MUST use the following format:

Thought: you should always think about what to do
Action: the name of the tool to use (must be one of [{tool_names}])
Action Input: the input to the tool
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)

When you have a final answer, you MUST use the format:

Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!
"""
        return f"{base_prompt}\n\n{react_instructions}"

    @exponential_backoff_retry(max_retries=3, base_delay=2.0)
    def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        """
        Internal method to call OpenAI API with retry logic.
        Uses stop sequences to prevent hallucination of tool outputs.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0,      # Deterministic output for tool usage
            stop=["Observation:"] # CRITICAL: Stop generating before hallucinating the result
        )
        return response.choices[0].message.content.strip()

    def _parse_output(self, llm_output: str) -> Union[str, Dict[str, str], None]:
        """
        Parses the LLM output to determine the next step.
        Returns:
            - str: If 'Final Answer' is found (return value).
            - dict: If 'Action' is found ({'tool': name, 'input': args}).
            - None: If parsing fails.
        """
        # Check for Final Answer first (highest priority)
        if "Final Answer:" in llm_output:
            return llm_output.split("Final Answer:")[-1].strip()
        
        # Check for Action
        match = self.action_pattern.search(llm_output)
        if match:
            action = match.group(1).strip()
            action_input = match.group(2).strip()
            # Clean up potential markdown code blocks around the input
            # LLMs sometimes wrap inputs in backticks (e.g. `input`).
            action_input = action_input.strip('`')
            return {"tool": action, "input": action_input}
        
        return None

    def prompt(self, problem_prompt: str, max_react_iterations: int) -> str:
        """
        The main execution loop (Reasoning -> Acting -> Observing).
        
        Args:
            problem_prompt: The user's query.
            max_react_iterations: Safety limit for the loop.
            
        Returns:
            The final answer string.
        """
        # Initialize Context Window
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": problem_prompt}
        ]
        
        iterations = 0
        
        while iterations < max_react_iterations:
            iterations += 1
            self.log.log(f"--- Iteration {iterations} ---")
            
            # 1. Thought Generation
            try:
                llm_response = self._call_llm(messages)
            except Exception as e:
                return f"Agent Failure: API Error could not be resolved: {e}"
            
            # Append Thought to History
            messages.append({"role": "assistant", "content": llm_response})
            self.log.log(f"DEBUG: LLM Output: {llm_response}")
            
            # 2. Parse Decision
            parsed = self._parse_output(llm_response)
            
            # Case A: Final Answer
            if isinstance(parsed, str):
                self.log.log("Final Answer received.")
                return parsed
            
            # Case B: Action Required
            elif isinstance(parsed, dict):
                tool_name = parsed['tool']
                tool_input = parsed['input']
                
                self.log.log(f"Action: {tool_name} | Input: {tool_input}")
                
                # 3. Tool Execution
                if tool_name in self.tools:
                    tool = self.tools[tool_name]
                    try:
                        # Execute the tool (Safe Execution Boundary)
                        observation_result = tool.use(tool_input)
                        
                        # Handle design-specified failure (returns False)
                        if observation_result is False:
                            observation = f"Error: Tool '{tool_name}' returned False. Please check your input format."
                        else:
                            observation = str(observation_result)
                            
                    except Exception as e:
                        # Catch unexpected runtime errors in the tool
                        observation = f"Error: Tool execution crashed: {e}"
                else:
                    # Hallucination handling
                    observation = f"Error: Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}"
                
                self.log.log(f"Observation: {observation}")
                
                # 4. Observation Injection
                # We inject the observation as a User message to simulate environment feedback
                messages.append({"role": "user", "content": f"Observation: {observation}"})
            
            # Case C: Parsing Failure
            else:
                self.log.log("WARNING: Failed to parse Action or Final Answer. Nudging agent.")
                # If the agent rambles without an action, we nudge it back on track
                messages.append({"role": "user", "content": "You did not specify an Action or Final Answer. Please continue using the specified format."})
                
        # Loop Exited without Answer
        return "Agent Failure: Maximum iterations reached without a Final Answer."