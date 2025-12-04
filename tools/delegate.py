from tools.tool import Tool
from util.app_context import App_Context
from util.prompt_loader import Prompt
from agent.Agent import Agent


class Delegate_Tool(Tool):
    name = "delegation-tool"
    description = """
    Accepts a single string, which includes a detailed description of the task you want to delegate 
    to an assistant AI. This AI has access to all the same tools as you do. It is recommended that 
    you use this tool to limit the amount of tokens in your own context window. The tasks you pass 
    this function must be clearly defined. For example, you might ask this tool to research a specific
    topic for you. Once your assistant finishes working, it will output a report on its findings and 
    actions. That report will be the output of this tool. 
    """
    alias = "Delegate"

    def __init__(self, cont: App_Context):
        self.ctx = cont

    def use(self, args: str):
        self.ctx.log.log("[DELEGATION TOOL] : Executing task.")
        agent = Agent(Prompt("delegate_prompt"), self.ctx.toolbox,
                   self.ctx.model_name, self.ctx.wallet.get("OPENAI"), self.ctx.log)
        
        self.ctx.log.log("[APPLICATION] : Beginning agentic execution...")
        out = agent.prompt("Begin helping.", self.ctx.max_iter)
        
        return out