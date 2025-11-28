from util.logs import Log
from tools.site_fetcher_tool import SiteFetcherTool




def test_fetch():
    print("\n\n" + "="*10 + "PERFORMING FETCH TEST" + "="*10)
    log = Log()
    tool = SiteFetcherTool(log)
    txt = tool.use("https://en.wikipedia.org/wiki/Apple")
    print("FOUND TEXT IN SITE: " + txt)