
from bot_browser import close_browser
from research_tool import Research_Tool, perform_research_tool_test_call
import asyncio
from agentic_source_finder import agentically_find_sources







def main():
    search_loop = asyncio.new_event_loop()
    research_tool = Research_Tool(search_loop)


    # brief test of the tool
    print("\n\n" + "="*50 + "\nTesting Resource Finder Tool\n" + "="*50) # header
    perform_research_tool_test_call(research_tool)

    # brief test of the AI
    print("\n\n" + "="*50 + "\nTesting Resource Finder Agent\n" + "="*50) # header
    dog_essay = ""
    with open("./res/dog_essay.txt", "r") as file:
        dog_essay = file.read()
    agentically_find_sources(dog_essay, research_tool)


    # # =========================================================================
    # # =================== Necessary Cleanup (DO NOT REMOVE) ===================
    # # =========================================================================
    print("\n\n" + "="*50 + "\nPerforming Cleanup\n" + "="*50) # header
    search_loop.run_until_complete(close_browser())
    search_loop.run_until_complete(asyncio.sleep(1))




if (__name__ == "__main__"):
    main()
