from core.interfaces.tools import AbstractTool


RATE_LIMITER = 1000 # ms between requests from the same site


class CreepyCrawly:
    def __init__(self, seed):
        self.to_visit = []
        self.seed = seed
        self.to_visit.append(self.seed)
        self.visited = []
        self.max_crawl
        
    
    def crawl_next():
        # pop a 