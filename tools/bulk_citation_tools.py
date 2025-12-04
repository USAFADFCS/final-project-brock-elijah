from util.logs import Log
from util.citations import get_citation_apa, get_citation_mla
from tools.tool import Tool
from util.works_cited import Works_Cited
from util.single_string_cleaner import clean_single_string
from util.app_context import App_Context

class Bulk_MLA_Citation_Tool(Tool):
    name = "bulk-mla-citation-tool"
    description = """
    Accepts no arguments. Creates an MLA citation for every site or resource we have visited on the 
    internet and a success message. Automatically adds
    the citations to our works cited tracker, so no further action is necessary to cite these source.
    Only call a single time per execution, after we are completely done fetching sources on the web.
    If any sources were used from the web, this tool MUST be called at the end of execution right 
    before we finish.
    """
    alias = "MLA Citer"

    def __init__(self, ctx : App_Context):
        self.logger = ctx.log
        self.works_cited = ctx.wc
        self.ctx = ctx

    def use(self, args: str):
        for url in self.ctx.all_visited_sites:
            self.logger.log(f"[MLA CITATION TOOL] : Creating MLA citation for [{url}]")
            try:
                citation = get_citation_mla(url)
                self.works_cited.cite("website", "mla", citation)
            except Exception as error:
                self.logger.log(f"[MLA CITATION TOOL] : Citation failed! {str(error)}")
        return "All sources successfully cited!"
    
class Bulk_APA_Citation_Tool(Tool):
    name = "bulk-apa-citation-tool"
    description = """
    Accepts no arguments. Creates an APA citation for every site or resource we have visited on the 
    internet and a success message. Automatically adds
    the citations to our works cited tracker, so no further action is necessary to cite these source.
    Only call a single time per execution, after we are completely done fetching sources on the web.
    If any sources were used from the web, this tool MUST be called at the end of execution right 
    before we finish.
    """
    alias = "APA Citer"

    def __init__(self, ctx : App_Context):
        self.logger = ctx.log
        self.works_cited = ctx.wc
        self.ctx = ctx

    def use(self, args: str):
        for url in self.ctx.all_visited_sites:
            self.logger.log(f"[APA CITATION TOOL] : Creating APA citation for [{url}]")
            try:
                citation = get_citation_apa(url)
                self.works_cited.cite("website", "apa", citation)
            except Exception as error:
                self.logger.log(f"[APA CITATION TOOL] : Citation failed! {str(error)}")
        return "All sources successfully cited!"