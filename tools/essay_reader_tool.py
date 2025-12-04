from util.logs import Log
from tools.tool import Tool
from util.app_context import App_Context

class Essay_Reader_Tool(Tool):
    name = "essay-reader-tool"
    description = """
    Does not require any arguments. Outputs the full text of the student written essay you 
    are supposed to be helping on.
    """
    alias = "Essay Reader"

    def __init__(self, cont: App_Context):
        self.ctx = cont

    def use(self, args: str):
        self.ctx.log.log("[ESSAY READER TOOL] : Reading full essay text to LLM.")
        return self.ctx.essay