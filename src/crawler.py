from core.interfaces.tools import AbstractTool
import asyncio
from pyppeteer import launch


RATE_LIMITER = 1000 # ms between requests from the same site


class CreepyCrawly:
    def __init__(self, seed, topic, max_crawl):
        self.to_visit = [] # the list of unvisited sites that we have discovered
        self.seed = seed # the url of the original site to start at
        self.to_visit.append((self.seed, 1)) # each element is a pair of (url, probability of relevance) 
        self.visited = [] # the list of sites visited
        self.max_crawl = max_crawl # the max number of sites to visit
        self.topic = topic # the topic to compare relevance to
        
        self.win = 
        
    
    def crawl_next():
        # pop the site off to_visit with the highest likelyhood of being relevant
        