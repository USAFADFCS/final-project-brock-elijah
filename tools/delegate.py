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
    actions. That report will be the output of this tool. Do not ask a delegate to do something that 
    you are unable to do, because it will not have any additional tools that you do not have. This is
    only to offload from your own context and prevent overly long thought chains.
    
    If you have access to this tool, you are not permitted to do any online research by yourself.
    You are required to delegate all research to this tool and ask it to return a report on a specific
    topic. You may include specific questions in your delegation command, but please combine questions
    which revolve around a specific topic so that you do not force your assistant to repeat the same
    research. Do not give your assistant a general question, such as "research key topics in the 
    essay." Instead, give it in such cases a specific topic you want help researching.
    
    Note that your assistant will not remember anything between uses of this tool. Its context 
    window is completely reset at the beginning of each call.
    """
    alias = "Delegate"

    def __init__(self, cont: App_Context):
        self.ctx = cont

    def use(self, args: str):
        self.ctx.log.log("[DELEGATION TOOL] : Executing task.")
        
        new_tools = []
        for tool in self.ctx.toolbox:
            if tool != self:
                new_tools.append(tool)
                
        agent = Agent(Prompt("delegate_prompt"), new_tools,
                   self.ctx.model_name, self.ctx.wallet.get("OPENAI"), self.ctx.log)
        
        out = agent.prompt(args, self.ctx.max_iter)
        
        self.ctx.log.log("[DELEGATION TOOL] : Task complete.")
        return out