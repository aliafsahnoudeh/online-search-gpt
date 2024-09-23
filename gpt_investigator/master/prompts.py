from datetime import datetime
from gpt_investigator.utils.enum import  ReportSource

def generate_search_queries_prompt(question: str, max_iterations: int=3,):
    """ Generates the search queries prompt for the given question.
    Args: 
        question (str): The question to generate the search queries prompt for
        max_iterations (int): The maximum number of search queries to generate
    
    Returns: str: The search queries prompt for the given question
    """        

    return f'Write {max_iterations} google search queries to conduct an answer to the question or topic delimited by three hashtags.' \
           f'pay a good attention to these points: \n' \
           f'- search queries should cover all aspects of the question and should be detailed and specific. \n' \
           f'- Use the current date if needed: {datetime.now().strftime("%B %d, %Y")}.\n' \
           f'- Also include in the queries specified task details such as locations, names, etc.\n' \
           f'- You must respond with a list of strings in the following format: ["query 1", "query 2", "query 3"].\n' \
           f'- The response should contain ONLY the list. \n' \
           f'The question or topic: \n' \
           f'###  {question} ###'


def generate_answer_prompt(question: str, context, report_source: str, total_words=1000):
    """ Generates the answer prompt for the given question.
    Args: question (str): The question to generate the answre prompt for
    Returns: str: The report prompt for the given question and research summary
    """    
    reference_prompt = ""
    if report_source == ReportSource.Web.value:
        reference_prompt = f"""
            You MUST write all used source urls at the end of the answer as references, and make sure to not add duplicated sources, but only one reference for each.
            Every url should be hyperlinked: [url website](url)
            Additionally, you MUST include hyperlinks to the relevant URLs wherever they are referenced in the ansewr, : 
        
            eg:    
                # Report Header
                
                This is a sample text. ([url website](url))
            """
    else:
        reference_prompt = f"""
            You MUST write all used source document names at the end of the answer as references, and make sure to not add duplicated sources, but only one reference for each."
        """
        

    return 'answer the question delimited by three starts using the information delimited by three hashtags.' \
           f' question: ***"{question}"***' \
           "pay attention to below points: \n" \
           "- The answer should be well structured, informative," \
           f" in depth and comprehensive, with facts and numbers if available and a minimum of {total_words} words.\n" \
           "You should strive to write the answer as long as you can using all relevant and necessary information provided.\n" \
           "You must write the answer with markdown syntax.\n " \
           "You MUST determine your own concrete and valid opinion based on the given information. Do NOT deter to general and meaningless conclusions.\n" \
           f"{reference_prompt}"\
            f"Cite search results using inline notations. Only cite the most \
            relevant results that answer the query accurately. Place these citations at the end \
            of the sentence or paragraph that reference them.\n"\
            f"Please do your best, this is very important to my career. " \
            f"Assume that the current date is {datetime.now().strftime('%B %d, %Y')}" \
            f"Information: ###" \
            f"{context}" \
            "### \n\n" \



def auto_agent_instructions():
    return """
        This task involves answering a question, regardless of its complexity or the availability of a definitive answer. The answer is conducted by a specific server, defined by its type and role, with each server requiring distinct instructions.
        Agent
        The server is determined by the field of the topic and the specific name of the server that could be utilized to research the topic provided. Agents are categorized by their area of expertise, and each server type is associated with a corresponding emoji.

        examples:
        task: "should I invest in apple stocks?"
        response: 
        {
            "server": "💰 Finance Agent",
            "agent_role_prompt: "You are a seasoned finance analyst AI assistant. Your primary goal is to compose comprehensive, astute, impartial, and methodically arranged answer based on provided data and trends."
        }
        task: "could reselling sneakers become profitable?"
        response: 
        { 
            "server":  "📈 Business Analyst Agent",
            "agent_role_prompt": "You are an experienced AI business analyst assistant. Your main objective is to produce comprehensive, insightful, impartial, and systematically structured answer based on provided business data, market trends, and strategic analysis."
        }
        task: "what are the most interesting sites in Tel Aviv?"
        response:
        {
            "server:  "🌍 Travel Agent",
            "agent_role_prompt": "You are a world-travelled AI tour guide assistant. Your main purpose is to draft engaging, insightful, unbiased, and well-structured answer on given locations, including history, attractions, and cultural insights."
        }
    """


def generate_summary_prompt(query, data):
    """ Generates the summary prompt for the given question and text.
    Args: question (str): The question to generate the summary prompt for
            text (str): The text to generate the summary prompt for
    Returns: str: The summary prompt for the given question and text
    """

    return f'{data}\n Using the above text, summarize it based on the following task or query: "{query}".\n If the ' \
           f'query cannot be answered using the text, YOU MUST summarize the text in short.\n Include all factual ' \
           f'information such as numbers, stats, quotes, etc if available. '

