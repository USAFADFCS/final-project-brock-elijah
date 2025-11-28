from util.logs import Log


REQUIRED_KEYS = [
    "GOOGLE_SEARCH",
    "GOOGLE_CX",
    "OPENAI"
]

class Key_Wallet:
    def __init__(self, logger : Log, pth="./.secret/keys.wallet"):
        self.pth = pth
        self.read_txt = ""
        self.logger = logger
        
        try:
            with open(self.pth, "r") as file:
                self.read_txt = file.read()
        except:
            self.logger.log("[API KEY WALLET] : ERROR, UNABLE TO LOAD KEYS FILE")
            self.logger.log("\tCREATING KEY FILE...")
            with open(self.pth, "w") as file:
                contents = ""
                for api in REQUIRED_KEYS:
                    contents += api + "=" + "\n"
                file.write(contents)
            self.logger.log("\tCREATED KEY FILE!")
            self.logger.log("\t\tPlease fill in the required api keys into the key file at: " + self.pth)
            self.logger.log("Exiting the program...")
            exit(0)
        
        self.keys = {}
        self.available_apis = []
        for line in self.read_txt.split("\n"):
            if line.strip() == "":
                continue
            api_name, api_key = line.split("=", 1)
            if (api_name.strip() == "" or api_key.strip() == ""):
                continue
            
            self.keys[api_name] = api_key
            self.available_apis.append(api_name)
        
        
        if not self._check_all_keys_exist():
            self.logger.log("[API KEY WALLET] : ERROR, could not find all necessary keys.")
            exit(0)
            
    def _check_all_keys_exist(self):
        self.logger.log("[API KEY WALLET] : Verifying all necessary API keys...")
        all_there = True
        for api in REQUIRED_KEYS:
            if api in self.available_apis:
                self.logger.log(f"\tFound [{api}]")
            else:
                self.logger.log(f"\tCould not find [{api}]")
                all_there = False
                
        return all_there

    def get(self, api_name):
        if api_name not in self.available_apis:
            self.logger.log(f"[API KEY WALLET] : ERROR, Could not find key for [{api_name}]")
            exit(0)
        return self.keys[api_name]
        