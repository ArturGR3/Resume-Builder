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


class ContactInfo(BaseModel):
    name: str = Field(description="The name of the person.")
    email: str = Field(description="The email address of the person.")
    possible_work_locations: List[str] = Field(description="""The possible work locations of the person relevant to the job requirements. e.g. United States(citizen): remote, Atlanta(GA), 
                                               EU(work permit): remote, Berlin(Germany)""")

class Summary(BaseModel):
    summary: str = Field(description="A short summary of the person's professional background and skills.")

class Media(BaseModel):
    linkedin_url: Optional[str] = Field(description="The LinkedIn URL of the person.")
    github_url: Optional[str] = Field(description="The GitHub URL of the person.")  
    medium_url: Optional[str] = Field(description="The Medium URL of the person.")
    website_url: Optional[str] = Field(description="The website URL of the person.")

class Experience(BaseModel):
    role: str = Field(description="The job title or position held. e.g. Software Engineer, Machine Learning Engineer.")
    company: str = Field(description="The name of the company or organization.")
    location: str = Field(description="The location of the company or organization. e.g. San Francisco, USA.")
    from_date: str = Field(description="The start date of the employment period. e.g., Aug 2023")
    to_date: str = Field(description="The end date of the employment period. e.g., Nov 2025")
    description: List[str] = Field(description="""A list of bullet points describing the work experience.""")

class Experiences(BaseModel):
    work_experience: List[Experience] = Field(description="Work experiences, including job title, company, location, dates, and description.")

class Education(BaseModel):
    degree: str = Field(description="The degree or qualification obtained and The major or field of study. e.g., Bachelor of Science in Computer Science.")
    university: str = Field(description="The name of the institution where the degree was obtained with location. e.g. Arizona State University, Tempe, USA")
    from_date: str = Field(description="The start date of the education period. e.g., Aug 2023")
    to_date: str = Field(description="The end date of the education period. e.g., May 2025")
    special_achievements: Optional[List[str]] = Field(description="""A list of special achievements or honors received during the education period. 
                                                      e.g., Dean's List, Honor Roll, GPA 4/4 etc.""")

class Educations(BaseModel):
    education: List[Education] = Field(description="Educations, including degree, university, dates, and special achievements.")

class Project(BaseModel):
    name: str = Field(description="The name of the project.")
    link: Optional[str] = Field(description="The link to the project.")   
    date: str = Field(description="The date of the project. e.g Aug 2023")
    key_technologies_concepts: List[str] = Field(description="""Key technologies and concepts used in the project.""")

class Certifications_Training(BaseModel):
    name: str = Field(description="The name of the certification or training (course, bootcamp etc.)")
    link: Optional[str] = Field(description="The link to the certification or training.")
    organization: str = Field(description="The organization that awarded the certification or training.")
    date: str = Field(description="The date of the certification or training.")
    key_technologies_concepts: List[str] = Field(description="""Key technologies and concepts used in the certification or training.""")
    project: Optional[Project] = Field(description="The project related to the certification or training.")
    information_source: Optional[Literal["resume", "knowledge base", "both"]] = Field(description="The source of the information about the certification.")
    
class Certifications_Trainings(BaseModel):
    certifications_trainings: List[Certifications_Training] = Field(description="Certifications or trainings, including name, organization, date, description, and information source.")  

class Projects(BaseModel):
    projects: List[Project] = Field(description="Projects, including name, date, link, and description.")

class SkillSection(BaseModel):
    name: str = Field(description="""name or title of the skills group such as programming languages, data science, tools & technologies, cloud & DevOps, full stack, or soft skills found 
                      in the resume.""")
    skills: List[str] = Field(description="Specific skills or competencies within the skill group, such as Python, JavaScript, C#, SQL in programming languages found in the resume.")

class SkillSections(BaseModel):
    skill_section: List[SkillSection] = Field(description="Skill sections, each containing a group of skills.")

class Resume(BaseModel):
    contact_info: ContactInfo = Field(description="Contact information of the person.")
    summary: Summary = Field(description="A short summary of the person's professional background and skills.")
    media: Media = Field(description="Media links of the person.")
    experiences: Experiences = Field(description="Work experiences of the person.")
    educations: Educations = Field(description="Educations of the person.")
    certifications_trainings: Certifications_Trainings = Field(description="Certifications or trainings of the person.")
    projects: Projects = Field(description="Projects of the person.")
    skill_sections: SkillSections = Field(description="Skill sections of the person.")

def main(file_path: str, provider: str = "openai", model: str = "gpt-4o-mini"):
    """
    Extract data from a resume file and save the response to a JSON file.
    """ 
    client = LLMFactory(provider=provider)
    if provider == "openai" and not model.startswith("gpt"):
        raise ValueError("Only OpenAI models starting with gpt are supported.")
    
    resume_text = extract_text(file_path)
    response = client.create_completion(
        model=model,
        messages=[
            {"role": "system", "content": "You are a resume parser. Parse the resume and extract the data according to the schema."},
            {"role": "user", "content": resume_text}
        ],
        response_model=Resume,
    )
    # save the response to a json file
    saved_path = f'resume_{model}_{date.today().strftime("%Y-%m-%d")}.json'
    
    with open(saved_path, 'w') as file:
        json.dump(response.model_dump(), file, indent=2)
    
    print(f"files saved to {saved_path}")

if __name__ == "__main__":
    main("./resumes/resume_md.md", "gpt-4o-mini")
    
    
# # open json file and print the data
# with open('resume_gpt-4o-mini_2024-10-28.json', 'r') as file:
#     data = json.load(file)
#     print(data)
    


