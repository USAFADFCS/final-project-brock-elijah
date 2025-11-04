
from bot_browser import close_browser
from research_tool import Research_Tool, perform_research_tool_test_call
import asyncio
from keyword_extractor_tool import Keyword_Extractor_Tool
from agentic_source_finder import agentically_find_sources


TESTS_TO_DO = {
    "resource_finder": False,
    "agent": True
}



def main():
    # load all the tools
    print("\n\n" + "="*50 + "\nLoading Tools\n" + "="*50) # header
    search_loop = asyncio.new_event_loop()
    print("Search loop created")
    research_tool = Research_Tool(search_loop)
    print("Research tool instantiated")
    keyword_tool = Keyword_Extractor_Tool("")
    print("Keyword extractor tool instantiated")


    # brief test of the tool
    if (TESTS_TO_DO["resource_finder"]):
        print("\n\n" + "="*50 + "\nTesting Resource Finder Tool\n" + "="*50) # header
        perform_research_tool_test_call(research_tool)
        research_tool.sources = [] # clear the sources

    if (TESTS_TO_DO["agent"]):
        # brief test of the AI
        print("\n\n" + "="*50 + "\nTesting Resource Finder Agent\n" + "="*50) # header
        dog_essay = ""
        with open("./res/dog_essay.txt", "r") as file:
            dog_essay = file.read()
        asyncio.run(agentically_find_sources(dog_essay, research_tool, 
                                                                keyword_tool))
        
        
        print("\n\n" + "="*50 + "\nResource Finder Agent Results\n" + "="*50) # header
        print(f"Found {len(research_tool.sources)} sources across the web")
        for index, source in enumerate(research_tool.sources):
            print(f"\t{index}. {source}")

    # # =========================================================================
    # # =================== Necessary Cleanup (DO NOT REMOVE) ===================
    # # =========================================================================
    print("\n\n" + "="*50 + "\nPerforming Cleanup\n" + "="*50) # header
    search_loop.run_until_complete(close_browser())
    search_loop.run_until_complete(asyncio.sleep(1))




if (__name__ == "__main__"):
    main()
