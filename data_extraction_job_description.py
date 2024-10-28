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

load_dotenv(find_dotenv(usecwd=True))

client = instructor.from_openai(openai.OpenAI())

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

def main(file_path: str, model: str = "gpt-4o-mini"):
    
    job_description_text = extract_text(file_path)
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a job description parser. Parse the job description and extract the data according to the schema."},
            {"role": "user", "content": job_description_text}
        ],
        response_model=JobDescription,
    )
    job_name = response.job_title
    
    # save the response to a json file
    saved_path = f'job_description_{model}_{date.today().strftime("%Y-%m-%d")}.json'
    
    with open(saved_path, 'w') as file:
        json.dump(response.model_dump_json(indent=2), file, indent=4)
    
    print(f"files saved to {saved_path}")
   

if __name__ == "__main__":
    
    main()
    
# with open('resume_gpt-4o-mini_2024-10-28.json', 'r') as file:
#     data = json.load(file)
#     print(data)
    