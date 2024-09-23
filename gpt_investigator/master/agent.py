import asyncio
import time

from gpt_investigator.config import Config
from gpt_investigator.context.compression import ContextCompressor
from gpt_investigator.document import DocumentLoader
from gpt_investigator.master.actions import *
from gpt_investigator.memory import Memory
from gpt_investigator.utils.enum import ReportSource


class GPTInvestigator:
    """
    Online Search GPT
    """

    def __init__(
        self,
        query: str,
        report_source=ReportSource.Web.value,
        source_urls=None,
        config_path=None,
        websocket=None,
        agent=None,
        role=None,
        parent_query: str = "",
        subtopics: list = [],
        visited_urls: set = set(),
        verbose: bool = True,
        context=[]
    ):
        """
        Initialize the Online Search GPT class.
        Args:
            query: str,
            source_urls
            config_path
            websocket
            agent
            role
            parent_query: str
            subtopics: list
            visited_urls: set
        """
        self.query: str = query
        self.agent: str = agent
        self.role: str = role
        self.report_source: str = report_source
        self.research_costs: float = 0.0
        self.cfg = Config(config_path)
        self.retriever = get_retriever(self.cfg.retriever)
        self.context = context
        self.source_urls = source_urls
        self.memory = Memory(self.cfg.embedding_provider)
        self.visited_urls: set[str] = visited_urls
        self.verbose: bool = verbose
        self.websocket = websocket

        # Only relevant for DETAILED REPORTS
        # --------------------------------------

        # Stores the main query of the detailed report
        self.parent_query = parent_query

        # Stores all the user provided subtopics
        self.subtopics = subtopics

    async def conduct_search(self):
        """
        Runs the Online Search GPT to conduct research
        """
        # Reset visited_urls and source_urls at the start of each research task
        self.visited_urls.clear()
        self.source_urls = []

        if self.verbose:
            await stream_output("logs", f"🔎 Starting the search for '{self.query}'...", self.websocket)
        
        # Generate Agent
        if not (self.agent and self.role):
            self.agent, self.role = await choose_agent(query=self.query, cfg=self.cfg,
                                                       parent_query=self.parent_query, cost_callback=self.add_costs)

        if self.verbose:
            await stream_output("logs", self.agent, self.websocket)
            

        # If specified, the researcher will use the given urls as the context for the research.
        if self.source_urls:
            self.context = await self.__get_context_by_urls(self.source_urls)
            
        elif self.report_source == ReportSource.Local.value:
            document_data = await DocumentLoader(self.cfg.doc_path).load()
            self.context = await self.__get_context_by_search(self.query, document_data)
        # Default web based research
        else:
            self.context = await self.__get_context_by_search(self.query)
        
        time.sleep(2)
        if self.verbose:
            await stream_output("logs", f"Finalized research step.\n💸 Total Research Costs: ${self.get_costs()}", self.websocket)

        return self.context

    async def write_report(self):
        """
        Writes the result

        Returns:
            str: The report
        """

        if self.verbose:
            await stream_output("logs", f"✍️ Writing summary for the search: {self.query}...", self.websocket)
            
        return await generate_report(
                query=self.query,
                context=self.context,
                agent_role_prompt=self.role,
                report_source=self.report_source,
                websocket=self.websocket,
                cfg=self.cfg,
                cost_callback=self.add_costs
            )
            

    async def __get_context_by_urls(self, urls):
        """
            Scrapes and compresses the context from the given urls
        """
        new_search_urls = await self.__get_new_urls(urls)
        if self.verbose:
            await stream_output("logs",
                            f"🧠 I will conduct my research based on the following urls: {new_search_urls}...",
                            self.websocket)
        scraped_sites = scrape_urls(new_search_urls, self.cfg)
        return await self.__get_similar_content_by_query(self.query, scraped_sites)

    async def __get_context_by_search(self, query, scraped_data: list = []):
        """
           Generates the context for the research task by searching the query and scraping the results
        Returns:
            context: List of context
        """
        context = []
        # Generate Sub-Queries including original query
        sub_queries = await get_sub_queries(query=query, agent_role_prompt=self.role,
                                            cfg=self.cfg,
                                            cost_callback=self.add_costs)

        if self.verbose:
            await stream_output("logs",
                                f"🧠 I will conduct my research based on the following queries: {sub_queries}...",
                                self.websocket)

        # Using asyncio.gather to process the sub_queries asynchronously
        context = await asyncio.gather(*[self.__process_sub_query(sub_query, scraped_data) for sub_query in sub_queries])
        return context

    async def __process_sub_query(self, sub_query: str, scraped_data: list = []):
        """Takes in a sub query and scrapes urls based on it and gathers context.

        Args:
            sub_query (str): The sub-query generated from the original query
            scraped_data (list): Scraped data passed in

        Returns:
            str: The context gathered from search
        """
        if self.verbose:
            await stream_output("logs", f"\n🔎 Running research for '{sub_query}'...", self.websocket)

        if not scraped_data:
            scraped_data = await self.__scrape_data_by_query(sub_query)

        content = await self.__get_similar_content_by_query(sub_query, scraped_data)

        if content and self.verbose:
            await stream_output("logs", f"📃 {content}", self.websocket)
        elif self.verbose:
            await stream_output("logs", f"🤷 No content found for '{sub_query}'...", self.websocket)
        return content

    async def __get_new_urls(self, url_set_input):
        """ Gets the new urls from the given url set.
        Args: url_set_input (set[str]): The url set to get the new urls from
        Returns: list[str]: The new urls from the given url set
        """

        new_urls = []
        for url in url_set_input:
            if url not in self.visited_urls:
                self.visited_urls.add(url)
                new_urls.append(url)
                if self.verbose:
                    await stream_output("logs", f"✅ Added source url to research: {url}\n", self.websocket)

        return new_urls

    async def __scrape_data_by_query(self, sub_query):
        """
        Runs a sub-query
        Args:
            sub_query:

        Returns:
            Summary
        """
        # Get Urls
        retriever = self.retriever(sub_query)
        search_results = retriever.search(
            max_results=self.cfg.max_search_results_per_query)
        new_search_urls = await self.__get_new_urls([url.get("href") for url in search_results])

        # Scrape Urls
        if self.verbose:
            await stream_output("logs", f"🤔 Researching for relevant information...\n", self.websocket)

        # Scrape Urls
        scraped_content_results = scrape_urls(new_search_urls, self.cfg)
        return scraped_content_results

    async def __get_similar_content_by_query(self, query, pages):
        if self.verbose:
            await stream_output("logs", f"📝 Getting relevant content based on query: {query}...", self.websocket)

        # Summarize Raw Data
        context_compressor = ContextCompressor(
            documents=pages,
            embeddings=self.memory.get_embeddings()
        )
        # Run Tasks
        return context_compressor.get_context(query=query, max_results=8, cost_callback=self.add_costs)

    ########################################################################################

    # GETTERS & SETTERS
    def get_source_urls(self) -> list:
        return list(self.visited_urls)

    def get_research_context(self) -> list:
        return self.context

    def get_costs(self) -> float:
        return self.research_costs

    def set_verbose(self, verbose: bool):
        self.verbose = verbose

    def add_costs(self, cost: int) -> None:
        if not isinstance(cost, float) and not isinstance(cost, int):
            raise ValueError("Cost must be an integer or float")
        self.research_costs += cost



    ########################################################################################

    # DETAILED REPORT

    async def write_introduction(self):
        # Construct Report Introduction from main topic research
        introduction = await get_report_introduction(self.query, self.context, self.role,
                                                     self.cfg, self.websocket, self.add_costs)

        return introduction

    async def get_subtopics(self):
        """
        This async function generates subtopics based on user input and other parameters.

        Returns:
          The `get_subtopics` function is returning the `subtopics` that are generated by the
        `construct_subtopics` function.
        """
        if self.verbose:
            await stream_output("logs", f"🤔 Generating subtopics...", self.websocket)

        subtopics = await construct_subtopics(
            task=self.query,
            data=self.context,
            config=self.cfg,
            # This is a list of user provided subtopics
            subtopics=self.subtopics,
        )

        if self.verbose:
            await stream_output("logs", f"📋Subtopics: {subtopics}", self.websocket)

        return subtopics
