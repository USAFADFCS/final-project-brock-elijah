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
from fairlib.core.interfaces.tools import AbstractTool

# --- Configuration Constants ---
# Use the Hugging Face Model Abstraction Layer (MAL) for Llama-3.2-3B-Instruct
MODEL_NAME = "meta-llama/Llama-3.2-3B-Instruct" 
# NOTE: In a real environment, you would need to ensure the adapter is configured
# to access this model via an API endpoint or a locally running inference server.
# For simplicity, we assume the HuggingFaceAdapter can access it.

def setup_huggingface_agent(
    research_tool: AbstractTool, 
    keyword_extractor_tool: AbstractTool
) -> SimpleAgent:
    """Initializes and configures the SimpleAgent with the Llama 3.2 model and tools."""

    # 1. Initialize the Model Abstraction Layer (MAL)
    # The HuggingFaceAdapter is used for models hosted on HF or via a compatible endpoint.
    # Note: Replace 'your_api_key' with a valid key or token if required for the model.
    llm = HuggingFaceAdapter(model_name=MODEL_NAME, api_key="placeholder")

    # 2. Define the Agent's Tool Registry and Executor
    tool_registry = ToolRegistry()
    tool_registry.register_tool(research_tool)
    tool_registry.register_tool(keyword_extractor_tool)
    executor = ToolExecutor(tool_registry)

    # 3. Configure the Agent's Brain (Planner and PromptBuilder)
    planner = ReActPlanner(llm, tool_registry)
    
    # 4. Customize the Agent's Role and Prompt (The "Personality")
    
    # Set a highly specific RoleDefinition
    planner.prompt_builder.role_definition = RoleDefinition(
        "You are an expert academic research assistant whose sole job is to find "
        "the most relevant reference sources for a provided essay. You must first "
        "use the keyword_extractor_tool, use those to guide the process of finding "
        "topics, and then use the research_tool with "
        "the resulting topics to find sources."
    )

    # Provide a few-shot example to guide the agent's workflow
    planner.prompt_builder.examples.clear()
    planner.prompt_builder.examples.append(
        Example(
            "# --- Example: Essay Source Finding Workflow ---\n"
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
            "system: Observation: None.\n"
            "assistant: "
            "Thought: I will convert the second keyword, 'contentious issue', into a topic to fit the context of the essay and use the research_tool to find sources.\n"
            "Action:\n"
            "tool_name: research_tool\n"
            "tool_input: AI in Education Contentions\n"
            "\n"
            "system: Observation: None.\n"
            "assistant: "
            "Thought: The research is complete and the research_tool now stores the final resources. I will indicate that research is complete.\n"
            "Action:\n"
            "tool_name: final_answer\n"
            "tool_input: All research complete!"
        )
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

async def agentically_find_sources(
    essay: str, 
    research_tool: Research_Tool, 
    keyword_extractor_tool: Keyword_Extractor_Tool
) -> str:
    """
    Uses the FAIR SimpleAgent with a Llama 3.2 model and two tools to find 
    reference sources for a given essay.
    """
    
    # 1. Instantiate the pre-configured agent
    agent = setup_huggingface_agent(research_tool, keyword_extractor_tool)
    
    # 2. Define the user's initial request
    user_request = (
        "Find the most relevant and high-quality reference sources for the "
        "following essay text. Use your tools to extract keywords and then "
        f"perform the search:\n\n---\n{essay}\n---"
    )
    
    # 3. Kick off the entire ReAct loop and await the final result
    print("--- Starting Agentic Research Pipeline ---")
    print(f"Agent Role: {agent.planner.prompt_builder.role_definition.content}")
    print(f"Model: {MODEL_NAME}")
    
    # The agent's arun method manages the entire sequence:
    # Keyword extraction -> Observation -> Search -> Observation -> Final Answer
    response = await agent.arun(user_request)
    
    print("--- Pipeline Complete ---")
    return response

# --- Note on Execution ---
# The function is asynchronous and must be called from an event loop, 
# typically via: asyncio.run(agentically_find_sources(...)) 
# or by using await inside an async function.
