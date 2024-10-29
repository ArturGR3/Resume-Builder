from src.data_extraction.data_extraction_job_description import main as extract_jd
from src.tailoring_resume.tailored_resume_json import main as tailor_resume
from src.pdf_creation.generate_resume import generate_resume
import os
from src.utils.llm_factory import LLMFactory

def process_job_application(job_description_file: str, 
                            resume_file: str, 
                            provider_for_parsing: str = "openai",
                            provider_for_tailoring: str = "anthropic",
                            model_for_parsing: str = "gpt-4o-mini",
                            model_for_tailoring: str = "claude-3-5-sonnet-20240620"):
    """
    Process a job application by:
    1. Extracting and parsing job description
    2. Tailoring resume to the job
    3. Generating PDF resume
    """
    
    if provider_for_parsing == "openai" and not model_for_parsing.startswith("gpt"):
        raise ValueError("Only OpenAI models starting with gpt are supported.")
    if provider_for_tailoring == "anthropic":
        model_for_tailoring = 'claude-3-5-sonnet-20240620'
    # Extract job description
    jd_json_path = extract_jd(job_description_file, provider_for_parsing, model_for_parsing)
    
    # Tailor resume
    resume_json_path = tailor_resume(resume_file, jd_json_path, provider_for_tailoring, model_for_tailoring)
    
    # Generate PDF
    generate_resume(resume_json_path)

if __name__ == "__main__":
    job_description_file = "jobs_results/Mozila_Staff_Machine_Learning_Engineer_Gen_AI_2024_10_28/mozila_jd.md"
    resume_file = "resumes/resume_gpt-4o-mini_2024-10-28.json"
    provider_for_parsing = "openai"
    provider_for_tailoring = "anthropic"
    model_for_parsing = "gpt-4o-mini"
    model_for_tailoring = "claude-3-5-sonnet-20240620"
    
    process_job_application(job_description_file, resume_file, provider_for_parsing, provider_for_tailoring, model_for_parsing, model_for_tailoring) 