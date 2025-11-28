



"""
As it turns out, the AI likes to add quotation marks around strings that it passes to tools that
accept a single string as an argument. This is terrible. The Google Search tool was returning nothing
because the search phrase in quotation marks had no exact matches. The Fetch tool was returning 
nothing because the url with quotations is not a real url at all. This fixes that, hopefully. 

Fingers crossed!
"""
def clean_single_string(inp : str):
    bad = ["\"", "'"]
    while inp[0] in bad:
        inp = inp[1:]
    while inp[-1] in bad:
        inp = inp[:-1]
    return inp