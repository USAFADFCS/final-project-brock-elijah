from util.app_context import App_Context
from tools.site_fetcher_tool import SiteFetcherTool




def test_fetch():
    print("\n\n" + "="*10 + "PERFORMING FETCH TEST" + "="*10)
    ctx = App_Context("")
    tool = SiteFetcherTool(ctx)
    # txt = tool.use("https://en.wikipedia.org/wiki/Apple") # does not require playwright
    txt = tool.use("https://pmc.ncbi.nlm.nih.gov/articles/PMC10218297/") # requires playwright
    print("FOUND TEXT IN SITE: " + txt)