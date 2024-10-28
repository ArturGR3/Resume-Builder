# Purpose of this script is to tailor the resume to the job description using LLM  
from typing import List, Optional, Literal
from datetime import date
from pydantic import BaseModel, Field
from dotenv import load_dotenv, find_dotenv
from src.utils.llm_factory import LLMFactory
import json
load_dotenv(find_dotenv(usecwd=True))

api_provider = "openai"
client = LLMFactory(api_provider) 

def extract_json(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        return json.load(file)

class ContactInfo(BaseModel):
    name: str = Field(description="The name of the person.")
    email: str = Field(description="The email address of the person.")
    location: Optional[List[str]] = Field(description="""Based on job description mention the work location.eg. USA remote (citizen), Berlin Germany (work visa)""")

class Summary(BaseModel):
    summary: str = Field(description="Sumamry of the resume based tailored to the job description.")

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
    description: List[str] = Field(description="""A list of bullet points describing the work experience tailored to the job description.
                                   Utilize STAR methodology (Situation, Task, Action, Result) implicitly within each bullet point.""", min_items=1, max_items=3)
    nice_to_add: Optional[List[str]] = Field(description="Something that is not present in the resume but will be good to add to make it more relevant to the job description.", min_items=0, max_items=5)

class Experiences(BaseModel):
    work_experience: List[Experience] = Field(description="Work experiences tailored to the job description.")

class Education(BaseModel):
    degree: str = Field(description="The degree or qualification obtained and The major or field of study. e.g., Bachelor of Science in Computer Science.")
    university: str = Field(description="The name of the institution where the degree was obtained with location. e.g. Arizona State University, Tempe, USA")
    from_date: str = Field(description="The start date of the education period. e.g., Aug 2023")
    to_date: str = Field(description="The end date of the education period. e.g., May 2025")
    special_achievements: Optional[List[str]] = Field(description="""A list of special achievements or honors received during the education period. 
                                                      e.g., Dean's List, Honor Roll, GPA 4/4 etc.""")

class Educations(BaseModel):
    education: List[Education] = Field(description="Educations, including degree, university, dates, and special achievements.")

class Certifications_Training(BaseModel):
    name: str = Field(description="The name of the certification or training (course, bootcamp etc.)")
    organization: str = Field(description="The organization that awarded the certification or training.")
    date: str = Field(description="The date of the certification or training.")
    description: Optional[str] = Field(description="""A short description of the certification or training based on the resume or 
                                       based on your knowledge base tailored to the job description.""")
    information_source: Optional[Literal["resume", "knowledge base", "both"]] = Field(description="The source of the information about the certification.")
    
class Certifications_Trainings(BaseModel):
    certifications_trainings: List[Certifications_Training] = Field(description="Certifications or trainings, including name, organization, date, description, and information source.")
    
class Project(BaseModel):
    name: str = Field(description="The name of the project.")
    date: str = Field(description="The date of the project. e.g Aug 2023")
    link: Optional[str] = Field(description="The link to the project.")   
    description: str = Field(description="A description of the project tailored to the job description.")

class Projects(BaseModel):
    projects: List[Project] = Field(description="Projects, including name, date, link, and description tailored to the job description.")

class SkillSection(BaseModel):
    name: str = Field(description="""name or title of the skills group such as programming languages, data science, tools & technologies, cloud & DevOps, full stack, or soft skills found 
                      in the resume tailored to the job description.""")
    skills: List[str] = Field(description="Specific skills or competencies within the skill group, such as Python, JavaScript, C#, SQL in programming languages found in the resume tailored to the job description.")
    nice_to_add: Optional[List[str]] = Field(description="Something that is not present in the resume but will be good to add to make it more relevant to the job description.")

class SkillSections(BaseModel):
    skill_section: List[SkillSection] = Field(description="Skill sections, each containing a group of skills tailored to the job description.")

class Resume(BaseModel):
    contact_info: ContactInfo = Field(description="Contact information of the person.")
    summary: Summary = Field(description="A short summary of the person's professional background and skills tailored to the job description.")
    media: Media = Field(description="Media links of the person.")
    experiences: Experiences = Field(description="Work experiences of the person tailored to the job description.")
    educations: Educations = Field(description="Educations of the person tailored to the job description.")
    certifications_trainings: Certifications_Trainings = Field(description="Certifications or trainings of the person tailored to the job description.")
    projects: Projects = Field(description="Projects of the person tailored to the job description.")
    skill_sections: SkillSections = Field(description="Skill sections of the person tailored to the job description.")
    nice_to_add: Optional[List[str]] = Field(description="Something that is not present in the resume but will be good to add to make it more relevant to the job description.", min_items=0, max_items=5)
    

def main(resume_path: str, job_description_path: str, model: client.settings.default_model):
    # extract json from resume and job description
    model = 'gpt-4o-2024-08-06'
    resume_path = 'resume_gpt-4o-mini_2024-10-28.json'
    job_description_path = 'job_description_gpt-4o-mini_2024-10-28.json'
    resume_json = extract_json(resume_path)
    job_description_json = extract_json(job_description_path)
    
    # create a prompt for the LLM
    system_prompt = f"""
    You are a resume expert with 15 years of experience in Software Engineering and Data Science. You are given a resume and a job description. You need to tailor the resume to the job description.
    1. Make sure to only use the information provided in the resume. Don't invent any information.
    2. Correct any spelling or grammar mistakes in the resume.
    3. You can remove the information that is not relevant to the job description.
    4. You can perephrase the information in the resume to make it more relevant to the job description making sure ATS can read it.
    
    return the output in JSON format.
    """

    user_prompt = f"""
    Resume: {resume_json}
    Job Description: {job_description_json}
    """
    
    response = client.create_completion(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_model=Resume,
    )
    
    return response


