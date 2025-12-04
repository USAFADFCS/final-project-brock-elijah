from util.application import Application_Instance
from tools.tool_registry import *


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
            available.append(Bulk_MLA_Citation_Tool.alias)
            available.append(Bulk_APA_Citation_Tool.alias)
            available.append(Delegate_Tool.alias)
        if ai_level >= 1:
            available.append(SiteFetcherTool.alias)
            available.append(GoogleSearchTool.alias)
            available.append(Leave_Note_Tool.alias)
        if ai_level >= 3:
            available.append(Essay_Reader_Tool.alias)
        
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
        app.run_agentic(query["instructions"], query["text"], 15)

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
        
        if (len(app.ctx.notes)):
            notes_str = "=" * 10 + "Notepad" + "=" * 10 + "\n\n"
            for note in app.ctx.notes:
                notes_str += f"[NOTE]:\n{note}"
            out["additional_downloadable_files"].append(
                {
                    "name": "AI_Notepad",
                    "extension": "txt",
                    "data": notes_str
                }
            )
        
        out["revised_text"] = app.ctx.essay
        
        
        self.has_run = True
        
        return out