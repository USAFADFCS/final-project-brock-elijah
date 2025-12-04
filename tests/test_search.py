from tools.google_search_tool import GoogleSearchTool
from util.app_context import App_Context


def test_search():
    print("\n\n" + "="*10 + "PERFORMING SEARCH TEST" + "="*10)
    ctx = App_Context("")


    print("Testing search tool...")
    tool = GoogleSearchTool(ctx)

    links = tool.use("apples as a fruit")
    print(links)