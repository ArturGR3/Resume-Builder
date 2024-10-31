import re
import PyPDF2
import os 
import json
from typing import List, Optional, Literal
from datetime import date
from pydantic import BaseModel, Field
import openai
import instructor
from dotenv import load_dotenv, find_dotenv
import sys
from src.utils.llm_factory import LLMFactory

load_dotenv(find_dotenv(usecwd=True))

def extract_text(file_path: str) -> str:
    _, file_extension = os.path.splitext(file_path)
    
    if file_extension.lower() == '.pdf':
        return extract_pdf_text(file_path)
    elif file_extension.lower() in ['.md', '.markdown']:
        return extract_markdown_text(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

def extract_pdf_text(pdf_path: str) -> str:
    resume_text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text = page.extract_text().split("\n")
            cleaned_text = [re.sub(r'[^\x00-\x7F]+', '', line) for line in text]
            resume_text += '\n'.join(cleaned_text)
    return resume_text

def extract_markdown_text(markdown_path: str) -> str:
    with open(markdown_path, 'r', encoding='utf-8') as file:
        return file.read()

class JobDescription(BaseModel):
    job_title: str = Field(description="The title of the job.")
    company_name: str = Field(description="The name of the company.")
    job_location: str = Field(description="The location of the job. eg. Remote, New York, London, etc.")
    job_type: str = Field(description="The type of the job. eg. Full-time, Part-time, Internship, etc.")
    job_duties_and_responsibilities: List[str] = Field(description="The purpose of the job and company, and the main duties and responsibilities.")
    required_qualifications: List[str] = Field(description="Including education, minimum experience, specific knowledge, skills, abilities, and any required licenses or certifications.")
    preferred_qualifications: List[str] = Field(description="Additional qualifications that could set a candidate apart.")
    job_benefits: List[str] = Field(description="The benefits of the job.")
    keywords: List[str] = Field(description="The keywords of the job that might be useful for the resume search.")

def main(file_path: str, provider: str = "openai", model: str = "gpt-4o-mini") -> str:
    client = LLMFactory(provider=provider)
    if provider == "openai" and not model.startswith("gpt"):
        raise ValueError("Only OpenAI models starting with gpt are supported.")
    
    job_description_text = extract_text(file_path)
    
    response = client.create_completion(
        model=model,
        messages=[
            {"role": "system", "content": "You are a job description parser. Parse the job description and extract the data according to the schema."},
            {"role": "user", "content": job_description_text}
        ],
        response_model=JobDescription,
    )
    
    # Create job results directory name
    job_name = response.job_title.replace(" ", "_")
    company_name = response.company_name.replace(" ", "_")
    result_dir = f'job_results/{company_name}_{job_name}_{date.today().strftime("%Y-%m-%d")}'
    
    # Create directory if it doesn't exist
    os.makedirs(result_dir, exist_ok=True)
    
    # Save the JSON response
    json_path = f'{result_dir}/job_description.json'
    with open(json_path, 'w') as file:
        json.dump(response.model_dump(), file, indent=2)
    
    # Save the original markdown file if it exists
    if file_path.endswith('.md'):
        import shutil
        shutil.copy2(file_path, f'{result_dir}/job_description_markdown_file.md')
    
    return json_path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Please provide a file path")
    
# with open('resume_gpt-4o-mini_2024-10-28.json', 'r') as file:
#     data = json.load(file)
#     print(data)
    