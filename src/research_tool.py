from fairlib import AbstractTool
from searcher import Searcher
import asyncio


class Reasearch_Tool(AbstractTool):
    name = "topic_source_finder"
    description = (
        "Researches sources across the web for a given topic. Use this ",
        "when you find a topic in the document which is suitable to search",
        "the web for additional sources on. The input **must** be a brief",
        "(no more than several words) description of a topic. Expect that",
        "this tool will keep track of all the sources found for you and will",
        "only return the total number of sources found up to this point.",
        "When you finish, these sources will be relayed to the user without",
        "you seeing them."
    )
    
    
    def __init__(self, searchLoop):
        self.loop = searchLoop
        super().__init__()
    
    def use(self, input_str):
        web_search = Searcher(input_str, loop=self.loop)
        
        urls = web_search.execute_sync()
        for url in urls:
            print(f"Found: {url}")
            
        return "Topic Research Successful!"





def perform_research_tool_test_call(tool_instance):
    tool_instance.use("implementing agentic ai")



