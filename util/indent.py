


def indent(txt : str, ind : int):
    out = ""
    for line in txt.split("\n"):
        out += ("\t" * ind) + line + "\n"
        
    return out