from tools.citation_tools import MLA_Citation_Tool, APA_Citation_Tool
from util.logs import Log
from util.works_cited import Works_Cited


# DEFAULT_URL = "https://www.bbc.com/news/articles/c751xw96e9yo"
DEFAULT_URL = "https://research.nhgri.nih.gov/dog_genome/about.shtml"

def test_mla():
    print("\n\n" + "="*10 + "PERFORMING CITE TEST (MLA)" + "="*10)
    log = Log()
    wc = Works_Cited()
    tool = MLA_Citation_Tool(log, wc)
    tool.use(DEFAULT_URL) # a random article
    result = wc.purge()
    print("Created citation: " + result)



def test_apa():
    print("\n\n" + "="*10 + "PERFORMING CITE TEST (APA)" + "="*10)
    log = Log()
    wc = Works_Cited()
    tool = APA_Citation_Tool(log, wc)
    tool.use(DEFAULT_URL) # a random article
    result = wc.purge()
    print("Created citation: " + result)

