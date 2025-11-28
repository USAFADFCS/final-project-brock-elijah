from tools.citation_tools import MLA_Citation_Tool, APA_Citation_Tool
from tools.site_fetcher_tool import SiteFetcherTool
from tools.google_search_tool import GoogleSearchTool
from util.application import Application_Instance

ALL_TOOLS = [
    MLA_Citation_Tool,
    APA_Citation_Tool,
    SiteFetcherTool,
    GoogleSearchTool
]


class Application_API:
    def __init__(self):
        self.has_run = False
    
    # to be connected to "mock get all tools" function in the web application
    def get_all_tools(self):
        tools = []
        for tool in ALL_TOOLS:
            tools.append(tool.alias)
        return tools
    
    # to be connected to "fetch allowed tools mock" function in the web application
    def get_allowed_tools(self, ai_level : int):
        available = []
        
        if True:
            available.append(MLA_Citation_Tool.alias)
            available.append(APA_Citation_Tool.alias)
        if ai_level >= 1:
            available.append(SiteFetcherTool.alias)
            available.append(GoogleSearchTool.alias)
        
        return available

    """
    to be connected to "mock server interaction" function in the web application
    
    Accepts query as object in form of 
    {
        "aiLevel": int,
        "instructions": str,
        "text": str,
        "tools": [str, str, ...]
    }
    
    Returns output as object in form of 
    {
        "revised_text" : str,
        "additional_downloadable_files": [
            {"name": str, "extension": str, "data": bytes},
            ...
        ],
        "transcript": str
    }
    """
    def run_analysis(self, query):
        app = Application_Instance(True)
        app.filter_down(query["tools"])
        app.run_agentic(query["instructions"], query["text"], 20)

        out = {}
        out["transcript"] = app.dump_log()
        out["additional_downloadable_files"] = []
        out["additional_downloadable_files"].append(
            {
                "name": "JSON_Works_Cited",
                "extension": "json",
                "data": app.dump_works_cited_json()
            }
        )
        out["additional_downloadable_files"].append(
            {
                "name": "TXT_Works_Cited",
                "extension": "txt",
                "data": app.dump_works_cited()
            }
        )
        
        
        self.has_run = True
        
        return out