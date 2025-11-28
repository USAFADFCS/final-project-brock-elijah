import time


class Log:
    def __init__(self, should_print=True):
        self.entries = [];
        self.saved = False;
        self.start_time = time.time()
        self.time_str = time.asctime(time.localtime(self.start_time))
        self.name = self.time_str.replace(" ", "_").replace(":", "") + ".log"
        self.as_string = ""
        self.should_print = should_print
        self.save_dir = "./logs/"
        
        self.log(f"[STARTED LOG AT {self.time_str}]\n")
    
    def log(self, mssg : str):
        self.entries.append(mssg)
        if (self.should_print):
            print(mssg)
            
        self.saved = False
        
    def save(self):
        self.as_string = ""
        for ent in self.entries:
            self.as_string += ent + "\n"
        
        with open(self.save_dir + self.name, "w") as file:
            file.write(self.as_string)