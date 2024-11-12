from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.markdown import Markdown
from rich.status import Status
import json
import tempfile
import os
from pathlib import Path
from typing import Optional
from datetime import date
import logging
from rich.logging import RichHandler
from datetime import datetime

from src.data_extraction.data_extraction_job_description import extract_job_description
from src.data_extraction.data_extraction_resume import extract_resume
from src.tailoring_resume.tailored_resume_json import tailor_resume
from src.pdf_creation.generate_resume import generate_resume

console = Console()

# Set up logging configuration right after imports
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging with both file and console handlers
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        # File handler with detailed logs
        logging.FileHandler(
            log_dir / f"resume_builder_{datetime.now().strftime('%Y-%m-%d')}.log"
        ),
        # Rich console handler for pretty output
        RichHandler(rich_tracebacks=True, markup=True)
    ]
)

logger = logging.getLogger("resume_builder")

def get_multiline_input() -> str:
    """
    Get text input from the user, stopping when the user types ':done' on a new line.
    """
    console.print("Enter/paste your text below. Type ':done' on a new line and press Enter when finished:", style="yellow")
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == ':done':
                break
            lines.append(line)
        except EOFError:
            break
    return '\n'.join(lines)

def file_check(file_path: str) -> bool:
    """
    Check if a file exists and log the result.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        bool: True if file exists, False otherwise
    """
    logger.info(f"Processing file: {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        console.print("❌ File not found!", style="bold red")
        return False
    return True

def process_job_description(provider: str, model: str) -> Optional[str]:
    """Process job description from text or file input."""
    console.print(Panel.fit("Job Description Processor", style="bold blue"))
    
    input_method = Prompt.ask(
        "How would you like to provide the job description?",
        choices=["text", "file"],
        default="text"
    )
    
    file_path = None
    try:
        if input_method == "text":
            text = get_multiline_input()
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
                temp_file.write(text)
                file_path = temp_file.name
        else:
            file_path = Prompt.ask("Enter the path to the job description file")

        with Status("[bold yellow]Processing job description...", spinner="dots") as status:
            _, file_extension = os.path.splitext(file_path)
            
            if file_extension.lower() == '.json':
                try:
                    with open(file_path, 'r') as f:
                        json_data = json.load(f)
                    
                    company_name = json_data.get("company_name", "unknown").replace(" ", "_")
                    today_date = date.today().strftime("%Y%m%d")
                    result_dir = Path(f'job_results/{company_name}_{today_date}')
                    result_dir.mkdir(parents=True, exist_ok=True)
                    
                    json_path = result_dir / "job_description.json"
                    with open(json_path, 'w') as f:
                        json.dump(json_data, f, indent=2)
                    
                except json.JSONDecodeError:
                    console.print("❌ Invalid JSON format!", style="bold red")
                    return None
            
            elif file_extension.lower() in ['.md', '.pdf']:
                json_path = extract_job_description(file_path, provider=provider, model=model)
            else:
                console.print(f"❌ Unsupported file type: {file_extension}", style="bold red")
                return None
            
            if json_path:
                console.print(f"\n✅ Job description processed and saved to: [bold green]{json_path}[/]")
                return str(json_path)
    
    finally:
        if input_method == "text" and file_path:
            os.unlink(file_path)
    
    return None

def process_resume(provider: str, model: str) -> Optional[str]:
    """Process resume from text or file input."""
    console.print(Panel.fit("\nResume Processing", style="bold blue"))
    
    resume_input = Prompt.ask(
        "How would you like to provide the resume?",
        choices=["text", "file"],
        default="file"
    )
    
    file_path = None
    try:
        if resume_input == "text":
            text = get_multiline_input()
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
                temp_file.write(text)
                file_path = temp_file.name
        else:
            file_path = Prompt.ask("Enter the path to the resume file")
        
        with Status("[bold yellow]Processing resume...", spinner="dots") as status:
            if not file_check(file_path):
                return None
            
            _, file_extension = os.path.splitext(file_path)
            
            if file_extension.lower() == '.json':
                try:
                    with open(file_path, 'r') as f:
                        json.load(f)
                    json_path = file_path
                except json.JSONDecodeError:
                    console.print("❌ Invalid JSON format!", style="bold red")
                    return None
            
            elif file_extension.lower() in ['.md', '.pdf']:
                json_path = extract_resume(file_path, provider=provider, model=model)
            else:
                console.print(f"❌ Unsupported file type: {file_extension}", style="bold red")
                return None
            
            if json_path:
                console.print(f"\n✅ Resume processed and saved to: [bold green]{json_path}[/]")
                return json_path
            
    finally:
        if resume_input == "text" and file_path:
            os.unlink(file_path)
    
    return None

def process_tailored_resume(resume_path: str, job_desc_path: str, 
                          provider: str, model: str) -> Optional[str]:
    """Generate tailored resume and optionally create PDF."""
    try:
        # Single status context for the entire tailoring process
        with Status("[bold yellow]Tailoring resume to job description...", spinner="dots") as status:
            # Generate tailored resume
            tailored_path = tailor_resume(
                resume_path=resume_path,
                job_description_path=job_desc_path,
                provider=provider,
                model=model
            )
            logger.info(f"Successfully tailored resume: {tailored_path}")
            console.print(f"\n✅ Tailored resume saved to: [bold green]{tailored_path}[/]")
            return tailored_path
            
    except Exception as e:
        logger.error(f"Failed to process tailored resume: {str(e)}", exc_info=True)
        console.print(f"\n❌ Failed to process: {str(e)}", style="bold red")
        return None

def generate_pdf_resume(tailored_path: str) -> Optional[str]:
    """Generate a PDF version of the tailored resume."""
    try:
        # Update status for PDF generation if needed
        with Status("[bold yellow]Generating PDF resume...", spinner="dots") as status:
            generate_resume(tailored_path)
            pdf_path = os.path.join(os.path.dirname(tailored_path), 'tailored_resume.pdf')
            logger.info(f"Successfully generated PDF: {pdf_path}")
            console.print(f"\n✅ PDF resume generated at: [bold green]{pdf_path}[/]")
            return pdf_path
    except Exception as e:
        logger.error(f"Failed to generate PDF resume: {str(e)}", exc_info=True)
        console.print(f"\n❌ Failed to generate PDF: {str(e)}", style="bold red")
        return None
            

# combined function to process job description, resume, and tailor resume to job description
def tailoring_resume_to_job_description(provider_for_parsing: str, 
                                      model_for_parsing: str,
                                      provider_for_resume: str,
                                      model_for_resume: str,
                                      provider_for_tailoring: str,
                                      model_for_tailoring: str) -> Optional[str]:
    """
    Orchestrates the complete process of processing a job description,
    processing a resume, and creating a tailored version.
    """
    try:
        # Step 1: Process job description
        job_desc_path = process_job_description(
            provider=provider_for_parsing,
            model=model_for_parsing
        )
        if not job_desc_path:
            return None

        # Step 2: Process resume (if user wants to)
        if Confirm.ask("\nWould you like to process a resume now?"):
            resume_path = process_resume(
                provider=provider_for_resume,
                model=model_for_resume
            )
            if not resume_path:
                return None

            # Step 3: Create tailored resume (if user wants to)
            if Confirm.ask("\nWould you like to tailor the resume to this job description?"):
                tailored_path = process_tailored_resume(
                    resume_path=resume_path,
                    job_desc_path=job_desc_path,
                    provider=provider_for_tailoring,
                    model=model_for_tailoring
                )
                if not tailored_path:
                    return None

                # Step 4: Generate PDF resume (if user wants to)
                if Confirm.ask("\nWould you like to generate a PDF version of the tailored resume?"):
                    pdf_path = generate_pdf_resume(tailored_path)
                    if not pdf_path:
                        return None

        return job_desc_path

    except Exception as e:
        logger.error("Unexpected error in tailoring_resume_to_job_description", exc_info=True)
        console.print(f"\n❌ An unexpected error occurred: {str(e)}", style="bold red")
        return None

if __name__ == "__main__":
    tailoring_resume_to_job_description() 