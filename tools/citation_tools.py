from util.logs import Log
from util.citations import get_citation_apa, get_citation_mla
from tools.tool import Tool
from util.works_cited import Works_Cited
from util.single_string_cleaner import clean_single_string
from util.app_context import App_Context

class MLA_Citation_Tool(Tool):
    name = "mla-citation-tool"
    description = """
    Accepts a single string argument, url of a site we want to cite using the MLA format. Creates
    an MLA citation for that webpage, and returns the string of that citation. Automatically adds
    the citation to our works cited tracker, so no further action is necessary to cite this source.
    """
    alias = "MLA Citer"

    def __init__(self, ctx : App_Context):
        self.logger = ctx.log
        self.works_cited = ctx.wc
        self.ctx = ctx

    def use(self, args: str):
        args = clean_single_string(args)
        self.logger.log(f"[MLA CITATION TOOL] : Creating MLA citation for [{args}]")
        try:
            citation = get_citation_mla(args)
            self.works_cited.cite("website", "mla", citation)
            return citation
        except Exception as error:
            self.logger.log(f"[MLA CITATION TOOL] : Citation failed! {str(error)}")
            return False
    
class APA_Citation_Tool(Tool):
    name = "apa-citation-tool"
    description = """
    Accepts a single string argument, url of a site we want to cite using the APA format. Creates
    an APA citation for that webpage, and returns the string of that citation. Automatically adds
    the citation to our works cited tracker, so no further action is necessary to cite this source.
    """
    alias = "APA Citer"

    def __init__(self, ctx : App_Context):
        self.logger = ctx.log
        self.works_cited = ctx.wc
        self.ctx = ctx

    def use(self, args: str):
        args = clean_single_string(args)
        self.logger.log(f"[APA CITATION TOOL] : Creating APA citation for [{args}]")
        try:
            citation = get_citation_mla(args)
            self.works_cited.cite("website", "apa", citation)
            return citation
        except Exception as error:
            self.logger.log(f"[APA CITATION TOOL] : Citation failed! {str(error)}")
            return False