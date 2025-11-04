# from get_page import get_page, wait_for_close
# import asyncio

# class Searcher:
#     def __init__(self, topic):
#         self.topic = topic
    
#     async def execute(self):
#         page = await get_page()
#         await page.goto("https://www.google.com")
#         await page.type('input[name="q"]', self.topic + "\n")
        

# async def main():
#     se = Searcher("apples")
#     await se.execute()
#     await wait_for_close(await get_page())


from bot_browser import get_page, user_close, ran_wait
from bot_browser import get_all_web_links, human_wait, close_browser
import asyncio
from concurrent.futures import ThreadPoolExecutor


class Searcher:
    def __init__(self, topic, engine_url="https://duckduckgo.com/", 
                 filters=["duckduckgo", "duck.ai"], loop=None):
        self.topic = topic
        self.engine_url = engine_url
        self.filters = filters
        self.loop = loop
        self.executor = ThreadPoolExecutor()
    
    def log(self, mssg):
        print(mssg)
        
    def _run_execute_async(self):
        if self.loop == None:
            print("ERROR: No event loop specified for synchronous execution of search.")
            exit(-1)
        return self.loop.run_until_complete(self.execute())

    def execute_sync(self):
        future = self.executor.submit(self._run_execute_async)
        return future.result()

    
    async def execute(self):
        page = await get_page()
        await page.goto(self.engine_url, wait_until="networkidle")
        
        self.log(f"Searcher arrived at {self.engine_url}")
        
        # Add human-like delay
        await human_wait(self.log)
        
        # Type with human-like delays
        for char in self.topic:
            await page.keyboard.type(text=char, delay=100)
        
        await asyncio.sleep(0.5)
        await page.keyboard.press('Enter')
        
        # Wait for results
        await page.wait_for_load_state("networkidle")
        
        
        # Add human-like delay
        await human_wait(self.log)
        
        unfilt_urls = await get_all_web_links(page)
        urls = []
        for url in unfilt_urls:
            keep = True
            for filt in self.filters:
                if filt in url:
                    keep = False
                    break
            if keep:
                urls.append(url)
                
        return urls





# ============= DEBUG ENVIRONMENT ===============
async def main():
    se = Searcher("apples")
    await se.execute()
    await close_browser()
    


if __name__ == "__main__":
    asyncio.run(main())
