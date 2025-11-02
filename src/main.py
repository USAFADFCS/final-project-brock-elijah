
from bot_browser import close_browser
from research_tool import Reasearch_Tool, perform_research_tool_test_call
import asyncio





def main():
    search_loop = asyncio.new_event_loop()
    research_tool = Reasearch_Tool(search_loop)

    # brief test of the tool (replace with actual agent using the tool)
    perform_research_tool_test_call(research_tool)




    # # =========================================================================
    # # =================== Necessary Cleanup (DO NOT REMOVE) ===================
    # # =========================================================================
    search_loop.run_until_complete(close_browser())
    search_loop.run_until_complete(asyncio.sleep(1))




if (__name__ == "__main__"):
    main()
