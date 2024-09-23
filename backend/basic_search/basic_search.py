from gpt_investigator.master.agent import GPTInvestigator
from fastapi import WebSocket


class BasicSearch():
    def __init__(self, query: str, report_source: str, source_urls, config_path: str, websocket: WebSocket):
        self.query = query
        self.report_source = report_source
        self.source_urls = source_urls
        self.config_path = config_path
        self.websocket = websocket
        
    async def run(self):
        # Initialize gpt_investigator
        gpt_investigator = GPTInvestigator(self.query, self.report_source, self.source_urls, self.config_path, self.websocket)
        
        # Run search
        await gpt_investigator.conduct_search()
        
        # and generate report        
        report = await gpt_investigator.write_report()
        
        return report