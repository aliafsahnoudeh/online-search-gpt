## ⚙️ Getting Started
### Installation
> **Step 0** - Install Python 3.11 or later. [See here](https://www.tutorialsteacher.com/python/install-python) for a step-by-step guide.

> **Step 1** - Download the project and navigate to its directory

```bash
git clone https://github.com/aliafsahnoudeh/online-search-gpt.git
cd online-search-gpt
```

> **Step 3** - Set up API keys using two methods: exporting them directly or storing them in a `.env` file.

For Linux/Windows temporary setup, use the export method:

```bash
export OPENAI_API_KEY={Your OpenAI API Key here}
export TAVILY_API_KEY={Your Tavily API Key here}
```

For a more permanent setup, create a `.env` file in the current `online-search-gpt` directory and input the env vars (without `export`).

- For LLM provider, we recommend **[OpenAI GPT](https://platform.openai.com/docs/guides/gpt)**, but you can use any other LLM model (including open sources). To learn how to change the LLM model, please refer to the [documentation](https://docs.gptr.dev/docs/online-search-gpt/llms) page. 
- For web search API, we recommend **[Tavily Search API](https://app.tavily.com)**, but you can also refer to other search APIs of your choice by changing the search provider in config/config.py to `duckduckgo`, `google`, `bing`, `serper`, `searx` and more. Then add the corresponding env API key.

### Quickstart

> **Step 1** - Install dependencies

```bash
pip install -r requirements.txt
```

> **Step 2** - Run the agent with FastAPI

```bash
python -m uvicorn main:app --reload
```

> **Step 3** - Go to http://localhost:8000 on any browser and enjoy researching!

<br />

This project is forked originall from [This repository](https://github.com/assafelovic/online-search-gpt.git)