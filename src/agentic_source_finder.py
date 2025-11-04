import asyncio
from typing import Awaitable, Any, Dict
from fairlib import (
    SimpleAgent,
    ReActPlanner,
    ToolExecutor,
    ToolRegistry,
    WorkingMemory,
    RoleDefinition,
    Example,
)
# NOTE: Assuming these custom tools are defined and implement AbstractTool
from research_tool import Research_Tool
from keyword_extractor_tool import Keyword_Extractor_Tool
from fairlib.modules.mal.huggingface_adapter import HuggingFaceAdapter
from fairlib.modules.mal.openai_adapter import OpenAIAdapter
from fairlib.core.interfaces.tools import AbstractTool
from fairlib import RoleDefinition
from dotenv import load_dotenv
import os
import torch
# --- Removed: from transformers import BitsAndBytesConfig ---
# --- Removed: import torch ---

# --- Configuration Constants ---
HUGGING_FACE_MODEL_NAME = "Qwen/Qwen3-4B-Instruct-2507" 
USE_HUGGINGFACE_API_KEY = True
HUGGING_FACE_QUANTIZED_FLAG = True

# if set to false, uses openAI model
# set to true to use huggingface model
LOCAL_TOGGLE = False

ROLE_DEFINITION = ("You are an expert academic research assistant whose sole job is to find "
    "the most relevant reference sources for a provided essay. You must first "
    "use the keyword_extractor_tool, use those to guide the process of finding "
    "topics, and then use the research_tool with "
    "the resulting topics to find sources.")

EXAMPLE_PROCESS = ("# --- Example: Essay Source Finding Workflow ---\n"
    "user: Find sources for the following essay: 'The rise of AI in education is a contentious issue...'\n"
    "assistant: "
    "Thought: The first step is to distill the long essay into searchable keywords. I will use the keyword_extractor_tool.\n"
    "Action:\n"
    "tool_name: keyword_extractor_tool\n"
    "tool_input: The rise of AI in education is a contentious issue...\n"
    "\n"
    "system: Observation: The extracted keywords are: ['AI in education', 'contentious issue'].\n"
    "assistant: "
    "Thought: I have the core keywords. I will convert 'AI' into a topic to fit the context of the essay and use the research_tool to find sources.\n"
    "Action:\n"
    "tool_name: research_tool\n"
    "tool_input: AI in education\n"
    "\n"
    "system: Observation: Topic Research For 'AI in education' Successful!\n"
    "assistant: "
    "Thought: I will convert the second keyword, 'contentious issue', into a topic to fit the context of the essay and use the research_tool to find sources.\n"
    "Action:\n"
    "tool_name: research_tool\n"
    "tool_input: AI in Education Contentions\n"
    "\n"
    "system: Observation: Topic Research For 'AI in Education Contentions' Successful!\n"
    "assistant: "
    "Thought: The research is complete and the research_tool now stores the final resources. I will indicate that research is complete.\n"
    "Action:\n"
    "tool_name: final_answer\n"
    "tool_input: All research complete!")

USE_EXAMPLES = True

OPEN_AI_MODEL_NAME = "gpt-4o"

# --- NEW CONSTANT FOR BUILT-IN QUANTIZATION ---
# FIX: Disabling quantization because the bitsandbytes dependency is failing 
# to find a supported device (GPU/CPU extension). Running in full precision.

def setup_huggingface_agent(
    research_tool: AbstractTool, 
    keyword_extractor_tool: Keyword_Extractor_Tool
) -> SimpleAgent:
    load_dotenv()
    # *** CHANGE: Get the API key from the environment variables ***
    hf_api_key = None
    if (USE_HUGGINGFACE_API_KEY):
        hf_api_key = os.getenv("HF_API_KEY")
        if not hf_api_key:
            raise ValueError("HF_API_KEY environment variable not found. Check your .env file.")
     
    
    """Initializes and configures the SimpleAgent with the Qwen model and tools."""

    # --- FIX: Use the generic 'quantized' flag ---
    # This dictionary now uses the general 'quantized' flag which the adapter 
    # should be designed to recognize and separate internally.
    model_loading_args = {
        "device_map": "auto", 
        "quantized": HUGGING_FACE_QUANTIZED_FLAG, # Use the general quantization flag (set to False)
        # Pass the auth_token explicitly
        "auth_token": hf_api_key if USE_HUGGINGFACE_API_KEY else None
    }

    if (not (torch.cuda.is_available())):
        model_loading_args["quantized"] = False
        print("================ WARNING ================")
        print("\tYour computer is terrible. It has no GPU. You will be stuck running")
        print("in slow mode (CPU). This is very bad.\n")
        print("\tIn the unlikely event that you do have a GPU, this warning means ")
        print("torch.cuda.is_available() returned False. You will need to uninstall")
        print("your current torch version and re-install the appropriate version for")
        print("your system. See the torch website for instructions.\n\n")
    # ------------------------------------------------------------------------

    # 1. Initialize the Model Abstraction Layer (MAL)
    # We unpack the simplified loading arguments.
    llm = HuggingFaceAdapter(
        model_name=HUGGING_FACE_MODEL_NAME, 
        **model_loading_args # Unpacking the loading arguments here
    )

    # 2. Define the Agent's Tool Registry and Executor
    tool_registry = ToolRegistry()
    tool_registry.register_tool(research_tool)
    tool_registry.register_tool(keyword_extractor_tool)
    executor = ToolExecutor(tool_registry)

    # 3. Configure the Agent's Brain (Planner and PromptBuilder)
    planner = ReActPlanner(llm, tool_registry)
    
    # 4. Customize the Agent's Role and Prompt (The "Personality")
    
    # Set a highly specific RoleDefinition
    planner.prompt_builder.role_definition = RoleDefinition(ROLE_DEFINITION)

    # Provide a few-shot example to guide the agent's workflow
    planner.prompt_builder.examples.clear()
    if USE_EXAMPLES:
        planner.prompt_builder.examples.append(
            Example(EXAMPLE_PROCESS)
        )

    # 5. Assemble the Agent
    agent = SimpleAgent(
        llm=llm,
        planner=planner,
        tool_executor=executor,
        # We use WorkingMemory to hold the context of the essay and the search results
        memory=WorkingMemory() 
    )
    
    return agent

def create_openai_agent(
    research_tool: AbstractTool, 
    keyword_extractor_tool: AbstractTool
) -> SimpleAgent:
    # 1. Configuration: Securely retrieve the OpenAI API key.
    # We follow the convention of using the OPENAI_API_KEY environment variable.
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY") 
    
    if not openai_api_key:
        # Raise an exception if the key is not found, ensuring security.
        raise ValueError("OPENAI_API_KEY environment variable not found. Check your .env file.")

    # No model loading args needed for OpenAIAdapter, as it is a remote API.
    # The adapter handles the remote API call logic internally.
    
    # 2. Initialize the Model Abstraction Layer (MAL)
    # Instantiate the OpenAIAdapter using the retrieved API key.
    llm = OpenAIAdapter(api_key=openai_api_key, model_name=OPEN_AI_MODEL_NAME)

    # 3. Define the Agent's Tool Registry and Executor (The Hands)
    tool_registry = ToolRegistry()
    # Register the tools provided in the function arguments.
    tool_registry.register_tool(research_tool)
    tool_registry.register_tool(keyword_extractor_tool)
    executor = ToolExecutor(tool_registry)

    # 4. Configure the Agent's Brain (Planner and PromptBuilder)
    # We use the ReActPlanner, the framework's default reasoning engine.
    planner = ReActPlanner(llm, tool_registry)
    
    # 5. Customize the Agent's Role and Prompt (The "Personality")
    
    # Set the same highly specific RoleDefinition as the template.
    planner.prompt_builder.role_definition = RoleDefinition(ROLE_DEFINITION)

    # Provide the same few-shot example to guide the agent's complex workflow (e.g., ReAct loop).
    planner.prompt_builder.examples.clear()
    if USE_EXAMPLES:
        planner.prompt_builder.examples.append(
            Example(EXAMPLE_PROCESS)
        )

    # 6. Assemble the Agent (The Orchestrator)
    # The SimpleAgent connects the LLM, Planner, Executor, and Memory into a functioning whole.
    agent = SimpleAgent(
        llm=llm,
        planner=planner,
        tool_executor=executor,
        memory=WorkingMemory() # Using short-term memory for conversation/results history
    )
    
    return agent

async def agentically_find_sources(
    essay: str, 
    research_tool: Research_Tool, 
    keyword_extractor_tool: Keyword_Extractor_Tool
) -> str:
    """
    Uses the FAIR SimpleAgent with a huggingface model and two tools to find 
    reference sources for a given essay.
    """
    
    # load the essay into the keyword finding tool
    keyword_extractor_tool.essay_text = essay

    # 1. Instantiate the pre-configured agent
    if (LOCAL_TOGGLE):
        print("USING LOCAL MODEL")
        agent = setup_huggingface_agent(research_tool, keyword_extractor_tool)
    else:
        print("USING OPENAI MODEL")
        agent = create_openai_agent(research_tool, keyword_extractor_tool)
    
    # 2. Define the user's initial request
    user_request = (
        "Find the most relevant and high-quality reference sources for the "
        "following essay text. Use your tools to extract keywords and then "
        f"perform the search:\n\n---\n{essay}\n---"
    )
    
    # 3. Kick off the entire ReAct loop and await the final result
    print("--- Starting Agentic Research Pipeline ---")
    role_def = agent.planner.prompt_builder.role_definition
    role_def : RoleDefinition
    print(f"Agent Role: {role_def.text}")
    if (LOCAL_TOGGLE):
        print(f"Model: {HUGGING_FACE_MODEL_NAME}")
    else:
        print(f"Model: {OPEN_AI_MODEL_NAME}")
    
    # The agent's arun method manages the entire sequence:
    # Keyword extraction -> Observation -> Search -> Observation -> Final Answer
    response = await agent.arun(user_request)
    
    print("--- Pipeline Complete ---")
    return response
