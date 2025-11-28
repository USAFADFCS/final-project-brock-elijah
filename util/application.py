from util.logs import Log
from tools.citation_tools import APA_Citation_Tool, MLA_Citation_Tool
from tools.google_search_tool import GoogleSearchTool
from tools.site_fetcher_tool import SiteFetcherTool
from agent.Agent import Agent
from util.works_cited import Works_Cited
from keys.wallet import Key_Wallet
from util.prompt_loader import Prompt
import json

class Application_Instance:
    
    def __init__(self, noisy=False):
        self.log = Log(noisy)
        self.works_cited = Works_Cited()
        self.wallet = Key_Wallet(self.log)
        self.tools = [
            APA_Citation_Tool(self.log, self.works_cited),
            MLA_Citation_Tool(self.log, self.works_cited),
            GoogleSearchTool(self.log, self.wallet),
            SiteFetcherTool(self.log)
        ]
        self.system_prompt = Prompt("system_prompt").txt
        self.target_model = "gpt-4.1-mini"
        
    def get_tool_aliases(self):
        registry = []
        for tool in self.tools:
            registry.append(tool.alias)
        return registry
    
    def filter_down(self, allowed_tool_aliases):
        allowed_tools = []
        for tool in self.tools:
            if tool.alias in allowed_tool_aliases:
                allowed_tools.append(tool)
        self.tools = allowed_tools
        
    def dump_log(self):
        self.log.save()
        return self.log.as_string
    
    def dump_works_cited(self):
        return self.works_cited.purge()
    
    def dump_works_cited_json(self):
        return json.dumps(self.works_cited.works, indent=2)
    
    def run_agentic(self, additional_prompting : str, essay : str, max_iter : int = 20):
        syst_prompt = self.system_prompt
        if (additional_prompting != ""):
            self.system_prompt += f"\nAdditionally, the user has instructed you: \"{additional_prompting}\""
        
        self.agent = Agent(syst_prompt, self.tools,
                           self.target_model, self.wallet.get("OPENAI"), self.log)
        
        self.log.log("[APPLICATION] : Beginning agentic execution...")
        out = self.agent.prompt(essay, max_iter)
        self.log.log("[APPLICATION] : Agentic execution complete!")
        self.log.log("\tOutput: " + out)
        
        return out