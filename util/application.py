from util.logs import Log
from agent.Agent import Agent
from util.prompt_loader import Prompt
from util.app_context import App_Context
from tools.tool_registry import *
import json
from util.ascii_filter import filter_non_ascii

class Application_Instance:
    
    def __init__(self, noisy=False):
        self.ctx = App_Context("No essay supplied.", noisy)
        self.tools = []
        for tool in ALL_TOOLS:
            self.tools.append(tool(self.ctx))
        self.system_prompt = Prompt("system_prompt").txt
        # self.target_model = "gpt-4.1-mini"
        self.target_model = "gpt-4o"
        
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
        self.ctx.log.save()
        return self.ctx.log.as_string
    
    def dump_works_cited(self):
        return self.ctx.wc.purge()
    
    def dump_works_cited_json(self):
        return json.dumps(self.ctx.wc.works, indent=2)
    
    def run_agentic(self, additional_prompting : str, essay : str, max_iter : int = 10):
        self.ctx.essay = filter_non_ascii(essay)
        self.ctx.toolbox = self.tools
        self.ctx.max_iter = max_iter
        self.ctx.model_name = self.target_model
        
        syst_prompt = self.system_prompt
        self.ctx.log.log(f"[APPLICATION] : Using prompt {syst_prompt[0:100].replace("\n", " ")}")
        tool_names = []
        for tool in self.tools:
            tool_names.append(tool.name)
        self.ctx.log.log(f"\tUsing tools: {json.dumps(tool_names)}")
        if (additional_prompting != ""):
            self.system_prompt += f"\nAdditionally, the user has instructed you: \"{additional_prompting}\""
        
        self.agent = Agent(syst_prompt, self.tools,
                           self.target_model, self.ctx.wallet.get("OPENAI"), self.ctx.log)
        
        self.ctx.log.log("[APPLICATION] : Beginning agentic execution...")
        out = self.agent.prompt("Begin helping.", max_iter)
        self.ctx.log.log("[APPLICATION] : Agentic execution complete!")
        self.ctx.log.log("\tOutput: " + out)
        
        return out