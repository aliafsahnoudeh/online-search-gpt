import os
import asyncio
import pytest
from gpt_investigator.master.agent import GPTInvestigator  # Ensure this path is correct
from dotenv import load_dotenv
load_dotenv()


# Define a common query and sources for testing
query = "What can you tell me about myself based on my documents?"

# Define the output directory
output_dir = "./outputs"

@pytest.mark.asyncio
async def test_gpt_searcher(report_type):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Create an instance of GPTInvestigator with report_source set to "documents"
    gpt_investigator = GPTInvestigator(query=query, report_source="documents")
    
    # Conduct search and write the report
    await gpt_investigator.conduct_search()
    report = await gpt_investigator.write_report()
    
    # Define the expected output filenames
    pdf_filename = os.path.join(output_dir, f"{report_type}.pdf")
    docx_filename = os.path.join(output_dir, f"{report_type}.docx")
    
    # Check if the PDF and DOCX files are created
    # assert os.path.exists(pdf_filename), f"PDF file not found for report type: {report_type}"
    # assert os.path.exists(docx_filename), f"DOCX file not found for report type: {report_type}"

    # Clean up the generated files (optional)
    # os.remove(pdf_filename)
    # os.remove(docx_filename)

if __name__ == "__main__":
    pytest.main()