from util.logs import Log
from util.works_cited import Works_Cited
from keys.wallet import Key_Wallet


class App_Context:
    def __init__(self, essay : str, verbose=True):
        self.log = Log(verbose)
        self.wc = Works_Cited()
        self.essay = essay
        self.wallet = Key_Wallet(self.log)
        self.all_visited_sites = []
        self.toolbox = []
        self.max_iter = 10
        self.model_name = ""
        self.notes = []