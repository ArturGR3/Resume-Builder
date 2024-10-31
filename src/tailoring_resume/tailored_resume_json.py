# Purpose of this script is to tailor the resume to the job description using LLM  
from typing import List, Optional, Literal
from datetime import date
from pydantic import BaseModel, Field
from dotenv import load_dotenv, find_dotenv
import json
import os
import sys

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)

# Change from relative import to absolute import
from src.utils.llm_factory import LLMFactory

load_dotenv(find_dotenv(usecwd=True))

def extract_json(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        return json.load(file)

class ContactInfo(BaseModel):
    name: str = Field(description="The name of the person.")
    email: str = Field(description="The email address of the person.")
    location: Optional[List[str]] = Field(description="Matching work locations from resume that align with job requirements with work authorization status.")

class Summary(BaseModel):
    summary: str = Field(description="A concise professional summary highlighting relevant qualifications, experience, and achievements that align with the target role.")

class Media(BaseModel):
    linkedin_url: Optional[str] = Field(description="The LinkedIn URL of the person.")
    github_url: Optional[str] = Field(description="The GitHub URL of the person.")  
    medium_url: Optional[str] = Field(description="The Medium URL of the person.")
    website_url: Optional[str] = Field(description="The website URL of the person.")

class Experience(BaseModel):
    role: str = Field(description="The job title or position held tailored to the job description.")
    company: str = Field(description="The name of the company or organization.")
    location: str = Field(description="The location of the company or organization. e.g. San Francisco, USA.")
    from_date: str = Field(description="The start date of the employment period. e.g., Aug 2023")
    to_date: str = Field(description="The end date of the employment period. e.g., Nov 2025")
    description: List[str] = Field(
        description="""A list of bullet points describing work experience, using STAR format (Situation, Task, Action, Result).
                      Each point should include quantified results and specific technical details if possible.
                      Example: 'Led ML pipeline development reducing processing time 40% and improving accuracy 15%'""",
        min_items=3,
        max_items=3
    )
    nice_to_add: Optional[List[str]] = Field(description="""Additional relevant skills, experiences or achievements that would strengthen alignment with the job 
                                             requirements but are not currently in the resume.""", min_items=0, max_items=5)

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
    education: List[Education] = Field(description="Educations, including degree, university, dates, and special achievements.", min_items=1, max_items=3)

class Project(BaseModel):
    name: str = Field(description="The name of the project.")
    date: str = Field(description="The date of the project. e.g Aug 2023")
    link: Optional[str] = Field(description="The link to the project.")   
    purpose: Optional[str] = Field(description="A concise 1-2 sentence description of what the project does and aims to achieve, derived from analyzing its key technologies and technical concepts.")
    key_technologies_concepts: Optional[str] = Field(description="""List of key technologies and concepts used in the project tailored to the job description.""")
    
class Certifications_Training(BaseModel):
    name: str = Field(description="The name of the certification or training (course, bootcamp etc.)")
    organization: str = Field(description="The organization that awarded the certification or training.")
    date: str = Field(description="The date of the certification or training.")
    certificate_link: Optional[str] = Field(description="The link to the certificate of the certification or training.")
    description: Optional[str] = Field(description="""A description summarizing the certification or training tailored to the job description.""")
    key_technologies_concepts: Optional[str] = Field(description="""List of key technologies and concepts used in the certification or training tailored to the job description.""")
    project: Optional[Project] = Field(description="The project related to the certification or training.")
    information_source: Optional[Literal["resume", "knowledge base", "both"]] = Field(description="The source of the information about the certification.")
    
class Certifications_Trainings(BaseModel):
    certifications_trainings: List[Certifications_Training] = Field(description="Certifications or trainings, including name, organization, date, description, and information source.")

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
    resume_title: str = Field(description="Short title starting with company name _ position name.")
    contact_info: ContactInfo = Field(description="Contact information of the person.")
    summary: Summary = Field(description="A short summary of the person's professional background and skills tailored to the job description.")
    media: Media = Field(description="Media links of the person.")
    experiences: Experiences = Field(description="Work experiences of the person tailored to the job description.")
    educations: Educations = Field(description="Educations of the person tailored to the job description.")
    certifications_trainings: Certifications_Trainings = Field(description="Certifications or trainings of the person tailored to the job description.")
    projects: Projects = Field(description="Projects of the person tailored to the job description.")
    skill_sections: SkillSections = Field(description="Skill sections of the person tailored to the job description.")
    nice_to_add: Optional[List[str]] = Field(description="Something that is not present in the resume but will be good to add to make it more relevant to the job description.", min_items=0, max_items=5)
    

def main(resume_path: str, job_description_path: str, provider: str ="anthropic", model: str = "claude-3-5-sonnet-20240620"):
    client = LLMFactory(provider=provider)
    if provider == "openai" and not model.startswith("gpt"):
        raise ValueError("Only OpenAI models starting with gpt are supported.")
    
    # extract json from resume and job description
    resume_json = extract_json(resume_path)
    job_description_json = extract_json(job_description_path)
    
    # Get the directory path from job_description_path
    result_dir = os.path.dirname(job_description_path)
    
    user_prompt = f"""
    You are an experienced resume expert specializing in Software Engineering and Data Science. 
    Your task is to optimize a candidate's resume for a specific job description, ensuring it passes ATS scans while engaging human readers. 
    Avoid anything that could cause Latex rendering issues like math equations, symbols, etc.

    Here is the candidate's resume:
    <resume>
    {resume_json}
    </resume>

    Here is the job description:
    <job_description>
    {job_description_json}
    </job_description>

    Please follow these steps to optimize the resume:

    1. Understand the job description and requirements.
    2. Identify matching skills and experiences from the resume.
    3. Tailor the resume content to the job description by:
        - Highlighting relevant quantifiable achievements. Do not invent any achievements.
        - Incorporating industry-specific keywords strategically.
        - Applying best practices (use active voice, strong action verbs, etc.).
        - Ensuring ATS compatibility while maintaining readability.
    4. Identify any missing information that would be useful for this application.

    After completing all steps, provide your output in JSON format. 
    Important: Only use information provided in the original resume. Do not invent or assume any additional details. 
    If there's specific information that might be useful for the job description but is missing from the resume, include it in the "nice_to_add" field.

    Begin your analysis now."""
    
    response = client.create_completion(
        model=model,
        messages=[
            # {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_model=Resume,
    )
    
    # Save tailored resume JSON
    json_path = f'{result_dir}/tailored_resume.json'
    with open(json_path, 'w') as file:
        json.dump(response.model_dump(), file, indent=2)
    
    return json_path

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Tailor resume to job description using LLM')
    parser.add_argument('--resume_path', type=str, required=True,
                      help='Path to the resume JSON file')
    parser.add_argument('--job_description_path', type=str, required=True,
                      help='Path to the job description JSON file')
    parser.add_argument('--model', type=str, default='claude-3-5-sonnet-20240620',
                      help='LLM model to use (default: claude-3-5-sonnet-20240620)')
    parser.add_argument('--provider', type=str, default='anthropic',
                      help='LLM provider to use (default: anthropic)')
    
    args = parser.parse_args()
    
    main(
        resume_path=args.resume_path,
        job_description_path=args.job_description_path,
        provider=args.provider,
        model=args.model
    )


# python src/tailoring_resume/tailored_resume_json.py \
#     --resume_path /home/artur/github/personal/Resume-Builder/resumes/resume_2024-10-31.json \
#     --job_description_path /home/artur/github/personal/Resume-Builder/job_results/Quantified.ai_AI_Engineer_2024-10-31/job_description.json \
#     --model claude-3-5-sonnet-20240620 \
#     --provider anthropic