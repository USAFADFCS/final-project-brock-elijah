from util.logs import Log
from tools.tool import Tool
from util.app_context import App_Context

class Leave_Note_Tool(Tool):
    name = "note-leaving-tool"
    description = """
    Allows you to leave a note for your human user. Because the user is very busy, leave concise
    bullet points whenever possible. Takes a single argument, the note to the user.
    
    NEVER use the note tool to write out corrected versions of the essay. This could get the user 
    in trouble for unauthorized use of AI. You may point out issues here, but you may not suggest any
    alternate versions for specific sentences in the user's essay.
    """
    alias = "Leave Notes"

    def __init__(self, cont: App_Context):
        self.ctx = cont

    def use(self, args: str):
        self.ctx.log.log("[NOTE LEAVER TOOL] : Transcribing note.")
        self.ctx.notes.append(args)
        return "Success! Your note has been stored for the user to read."