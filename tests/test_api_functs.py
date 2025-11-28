from web_api.api_functions import Application_API
import json
from util.prompt_loader import Prompt
from util.indent import indent


def test_api_functs():
    print("\n\n" + "="*10 + "PERFORMING API FUNCTIONS TEST" + "="*10)
    
    api = Application_API()
    all_tools = api.get_all_tools()
    allowed = api.get_allowed_tools(1)
    
    print(f"\tAllowed Tools : {json.dumps(allowed)}")
    print(f"\tAll Tools     : {json.dumps(all_tools)}")
    
    query = {
        "aiLevel": 1,
        "instructions": Prompt("research_prompt").txt,
        "text": Prompt("test_essay").txt,
        "tools": allowed
    }
    
    print(f"\tTesting Query: ")
    print(f"{indent(json.dumps(query, indent=2), 2)}")
    
    out = api.run_analysis(query)
    print(f"\n\n\tGot Result: ")
    print(indent(json.dumps(out, indent=2), 2))