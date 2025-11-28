



class Prompt:
    def __init__(self, name : str):
        self.name = name
        self.path = "./prompts/" + self.name + ".txt"
        self.txt = ""
        with open(self.path, "r") as file:
            self.txt = file.read()
    