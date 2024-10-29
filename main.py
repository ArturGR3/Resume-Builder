from src.data_extraction.data_extraction_job_description import main as extract_jd
from src.tailoring_resume.tailored_resume_json import main as tailor_resume
from src.pdf_creation.generate_resume import generate_resume
import os

def process_job_application(job_description_file: str, 
                            resume_file: str, 
                            model_for_parsing: str = "gpt-4o-mini",
                            model_for_tailoring: str = "gpt-4o"):
    """
    Process a job application by:
    1. Extracting and parsing job description
    2. Tailoring resume to the job
    3. Generating PDF resume
    """
    # Extract job description
    jd_json_path = extract_jd(job_description_file, model_for_parsing)
    
    # Tailor resume
    resume_json_path = tailor_resume(resume_file, jd_json_path, model_for_tailoring)
    
    # Generate PDF
    generate_resume(resume_json_path)

if __name__ == "__main__":
    job_description_file = "jobs_results/Mozila_Staff_Machine_Learning_Engineer_Gen_AI_2024_10_28/mozila_jd.md"
    resume_file = "resumes/resume_gpt-4o-mini_2024-10-28.json"
    model_for_parsing = "gpt-4o-mini"
    model_for_tailoring = "gpt-4o"
    
    process_job_application(job_description_file, resume_file, model_for_parsing, model_for_tailoring) 