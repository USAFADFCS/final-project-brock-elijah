from tools.google_search_tool import GoogleSearchTool
from keys.wallet import Key_Wallet
from util.logs import Log


def test_search():
    print("\n\n" + "="*10 + "PERFORMING SEARCH TEST" + "="*10)
    log = Log()
    wallet = Key_Wallet(log)


    print("Testing search tool...")
    tool = GoogleSearchTool(log, wallet)

    links = tool.use("apples as a fruit")
    print(links)