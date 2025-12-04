from tools.citation_tools import MLA_Citation_Tool, APA_Citation_Tool
from util.app_context import App_Context


# DEFAULT_URL = "https://www.bbc.com/news/articles/c751xw96e9yo"
DEFAULT_URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC10218297" # requires playwright fallback

def test_mla():
    print("\n\n" + "="*10 + "PERFORMING CITE TEST (MLA)" + "="*10)
    ctx = App_Context("")
    tool = MLA_Citation_Tool(ctx)
    tool.use(DEFAULT_URL) # a random article
    result = ctx.wc.purge()
    print("Created citation: " + result)



def test_apa():
    print("\n\n" + "="*10 + "PERFORMING CITE TEST (APA)" + "="*10)
    ctx = App_Context("")
    tool = APA_Citation_Tool(ctx)
    tool.use(DEFAULT_URL) # a random article
    result = ctx.wc.purge()
    print("Created citation: " + result)

