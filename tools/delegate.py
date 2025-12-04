from tools.tool import Tool
from util.app_context import App_Context
from util.prompt_loader import Prompt
from agent.Agent import Agent


class _Take_Delegate_Note_Tool(Tool):
    name = "note-recorder-tool"
    description = """
    Accepts a single argument, the note you want to take. All of these notes will be compiled 
    together after you are done and passed to the head AI. Use this tool to record summaries of any 
    information you believe is relevant to your task. Keep notes fairly detailed but also concise 
    and to the point. This tool will return a confirmation message when done.
    """
    alias = "Delegate Note Taker"

    def __init__(self, ctx : App_Context):
        self.notes = []
        self.ctx = ctx

    def use(self, args: str):
        self.ctx.log.log("[DELEGATE NOTE RECORDER TOOL] : Note successfully recorded.")
        return "Success! Your note will be passed on to the head AI when you are done."

class Delegate_Tool(Tool):
    name = "delegation-tool"
    description = """
    Accepts a single string, which includes a detailed description of the task you want to delegate 
    to an assistant AI. This AI has access to all the same tools as you do. It is recommended that 
    you use this tool to limit the amount of tokens in your own context window. The tasks you pass 
    this function must be clearly defined. Once your assistant finishes working, it will output a report on its findings and 
    actions. That report will be the output of this tool. Do not ask a delegate to do something that 
    you are unable to do, because it will not have any additional tools that you do not have. This is
    only to offload from your own context and prevent overly long thought chains.
    
    If you have access to this tool, you are not permitted to do any online research by yourself.
    This includes performing internet searches or requesting webpages.
    You are required to delegate all research to this tool and ask it to return a report on a specific
    topic. You may include specific questions in your delegation command, but please combine questions
    which revolve around a specific topic so that you do not force your assistant to repeat the same
    research. Do not give your assistant a general question, such as "research key topics in the 
    essay." Instead, give it in such cases a specific topic you want help researching.
    
    Examples of valid use for this tool include asking the delegate to research a specific topic, 
    asking your delegate to check the grammar of the essay, or asking your delegate to make revisions 
    for a specific type of mistake.
    
    Note that your assistant will not remember anything between uses of this tool. Its context 
    window is completely reset at the beginning of each call.
    """
    alias = "Delegate"

    def __init__(self, cont: App_Context):
        self.ctx = cont

    def use(self, args: str):
        self.ctx.log.log("[DELEGATION TOOL] : Executing task.")
        notepad = _Take_Delegate_Note_Tool(self.ctx)
        
        new_tools = [notepad]
        for tool in self.ctx.toolbox:
            if tool != self:
                new_tools.append(tool)
                
        agent = Agent(Prompt("delegate_prompt"), new_tools,
                   self.ctx.model_name, self.ctx.wallet.get("OPENAI"), self.ctx.log)
        
        out = agent.prompt(args, self.ctx.max_iter)
        
        out += "\n"
        for note in notepad.notes:
            out += f"\t[NOTE] : {note}"
        
        self.ctx.log.log("[DELEGATION TOOL] : Task complete.")
        return out