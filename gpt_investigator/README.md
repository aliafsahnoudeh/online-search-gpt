# 🔎 Online Search GPT
[![Official Website](https://img.shields.io/badge/Official%20Website-gptr.dev-blue?style=for-the-badge&logo=world&logoColor=white)](https://gptr.dev)
[![Discord Follow](https://dcbadge.vercel.app/api/server/QgZXvJAccX?style=for-the-badge)](https://discord.com/invite/QgZXvJAccX)

[![GitHub Repo stars](https://img.shields.io/github/stars/assafelovic/online-search-gpt?style=social)](https://github.com/assafelovic/online-search-gpt)
[![Twitter Follow](https://img.shields.io/twitter/follow/tavilyai?style=social)](https://twitter.com/tavilyai)
[![PyPI version](https://badge.fury.io/py/online-search-gpt.svg)](https://badge.fury.io/py/online-search-gpt)

**Online Search GPT is an autonomous agent designed for comprehensive online research on a variety of tasks.** 

The agent can produce detailed, factual and unbiased research reports, with customization options for focusing on relevant resources, outlines, and lessons. Inspired by the recent [Plan-and-Solve](https://arxiv.org/abs/2305.04091) and [RAG](https://arxiv.org/abs/2005.11401) papers, Online Search GPT addresses issues of speed, determinism and reliability, offering a more stable performance and increased speed through parallelized agent work, as opposed to synchronous operations.

**Our mission is to empower individuals and organizations with accurate, unbiased, and factual information by leveraging the power of AI.**

#### PIP Package
> **Step 0** - Install Python 3.11 or later. [See here](https://www.tutorialsteacher.com/python/install-python) for a step-by-step guide.
> **Step 1** - install Online Search GPT package [PyPI page](https://pypi.org/project/online-search-gpt/)
```bash
$ pip install online-search-gpt
```
> **Step 2** - Create .env file with your OpenAI Key and Tavily API key or simply export it
```bash
$ export OPENAI_API_KEY={Your OpenAI API Key here}
```
```bash
$ export TAVILY_API_KEY={Your Tavily API Key here}
```
> **Step 3** - Start Coding using Online Search GPT in your own code, example:
```python
from gpt_investigator import GPTInvestigator
import asyncio


async def get_report(query: str, report_type: str) -> str:
    researcher = GPTInvestigator(query, report_type)
    report = await researcher.run()
    return report

if __name__ == "__main__":
    query = "what team may win the NBA finals?"
    report_type = "research_report"

    report = asyncio.run(get_report(query, report_type))
    print(report)

```


