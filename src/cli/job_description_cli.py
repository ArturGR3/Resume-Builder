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
import time
from datetime import date
import logging
from rich.logging import RichHandler
from datetime import datetime

from src.data_extraction.data_extraction_job_description import main as extract_job_description
from src.data_extraction.data_extraction_resume import main as extract_resume
from src.tailoring_resume.tailored_resume_json import main as tailor_resume
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

def process_file(file_path: str) -> Optional[str]:
    logger.info(f"Processing file: {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        console.print("❌ File not found!", style="bold red")
        return None
    
    _, file_extension = os.path.splitext(file_path)
    
    if file_extension.lower() == '.json':
        # Handle JSON file
        try:
            with open(file_path, 'r') as f:
                json_data = json.load(f)
            
            # Create directory and save JSON
            job_name = json_data.get("job_title", "unknown").replace(" ", "_")
            company_name = json_data.get("company_name", "unknown").replace(" ", "_")
            result_dir = Path(f'job_results/{company_name}_{job_name}')
            result_dir.mkdir(parents=True, exist_ok=True)
            
            json_path = result_dir / "job_description.json"
            with open(json_path, 'w') as f:
                json.dump(json_data, f, indent=2)
            
            return str(json_path)
            
        except json.JSONDecodeError:
            console.print("❌ Invalid JSON format in file!", style="bold red")
            return None
    
    elif file_extension.lower() in ['.md', '.pdf']:
        # Process through AI
        return extract_job_description(file_path)
    
    else:
        console.print(f"❌ Unsupported file type: {file_extension}", style="bold red")
        return None

def process_resume_file(file_path: str) -> Optional[str]:
    logger.info(f"Processing resume file: {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"Resume file not found: {file_path}")
        console.print("❌ File not found!", style="bold red")
        return None
    
    _, file_extension = os.path.splitext(file_path)
    
    if file_extension.lower() == '.json':
        # For JSON files, validate the format and return the original path
        try:
            with open(file_path, 'r') as f:
                json.load(f)  # Just validate JSON format
            return file_path
            
        except json.JSONDecodeError:
            console.print("❌ Invalid JSON format in file!", style="bold red")
            return None
    
    elif file_extension.lower() in ['.md', '.pdf']:
        # Process through AI and create new file
        return extract_resume(file_path)
    
    else:
        console.print(f"❌ Unsupported file type: {file_extension}", style="bold red")
        return None

def process_resume() -> Optional[str]:
    console.print(Panel.fit("\nResume Processing", style="bold blue"))
    
    resume_input = Prompt.ask(
        "How would you like to provide the resume?",
        choices=["text", "file"],
        default="file"
    )
    
    json_path = None
    
    if resume_input == "text":
        text = get_multiline_input()
        
        with Status("[bold yellow]Processing resume...", spinner="dots") as status:
            # Save text to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
                temp_file.write(text)
                temp_path = temp_file.name
            
            try:
                json_path = extract_resume(temp_path)
                console.print(f"\n✅ Resume processed and saved to: [bold green]{json_path}[/]")
            finally:
                os.unlink(temp_path)
    
    else:  # file
        file_path = Prompt.ask("Enter the path to the resume file")
        
        with Status("[bold yellow]Processing file...", spinner="dots") as status:
            json_path = process_resume_file(file_path)
            if json_path:
                console.print(f"\n✅ Resume processed and saved to: [bold green]{json_path}[/]")
    
    return json_path

def process_job_description():
    try:
        console.print(Panel.fit("Job Description Processor", style="bold blue"))
        
        input_method = Prompt.ask(
            "How would you like to provide the job description?",
            choices=["text", "file"],
            default="text"
        )
        
        job_desc_path = None
        
        if input_method == "text":
            text = get_multiline_input()
            
            with Status("[bold yellow]Processing job description...", spinner="dots") as status:
                # Save text to temporary file
                status.update("[bold yellow]Creating temporary file...")
                with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
                    temp_file.write(text)
                    temp_path = temp_file.name
                
                try:
                    status.update("[bold yellow]Extracting information using AI...")
                    job_desc_path = extract_job_description(temp_path)
                    console.print(f"\n✅ Job description processed and saved to: [bold green]{job_desc_path}[/]")
                finally:
                    status.update("[bold yellow]Cleaning up temporary files...")
                    os.unlink(temp_path)
        
        else:  # file
            file_path = Prompt.ask("Enter the path to the job description file")
            
            with Status("[bold yellow]Processing file...", spinner="dots") as status:
                job_desc_path = process_file(file_path)
                if job_desc_path:
                    console.print(f"\n✅ Job description processed and saved to: [bold green]{job_desc_path}[/]")
        
        if job_desc_path:
            if Confirm.ask("\nWould you like to process a resume now?"):
                resume_path = process_resume()
                
                if resume_path and Confirm.ask("\nWould you like to tailor the resume to this job description?"):
                    # Separate status context for tailoring
                    with Status("[bold yellow]Tailoring resume to job description...", spinner="dots") as status:
                        try:
                            tailored_path = tailor_resume(
                                resume_path=resume_path,
                                job_description_path=job_desc_path
                            )
                            logger.info(f"Successfully tailored resume: {tailored_path}")
                            console.print(f"\n✅ Tailored resume saved to: [bold green]{tailored_path}[/]")
                        except Exception as e:
                            logger.error(f"Failed to tailor resume: {str(e)}", exc_info=True)
                            console.print(f"\n❌ Failed to tailor resume: {str(e)}", style="bold red")
                            return
                    
                    # Separate PDF generation step outside the tailoring status
                    if Confirm.ask("\nWould you like to generate a PDF version of the tailored resume?"):
                        with Status("[bold yellow]Generating PDF resume...", spinner="dots") as status:
                            try:
                                generate_resume(tailored_path)
                                pdf_path = os.path.join(os.path.dirname(tailored_path), 'tailored_resume.pdf')
                                logger.info(f"Successfully generated PDF: {pdf_path}")
                                console.print(f"\n✅ PDF resume generated at: [bold green]{pdf_path}[/]")
                            except Exception as e:
                                logger.error(f"Failed to generate PDF: {str(e)}", exc_info=True)
                                console.print(f"\n❌ Failed to generate PDF: {str(e)}", style="bold red")
    except Exception as e:
        logger.error("Unexpected error in process_job_description", exc_info=True)
        raise

def main():
    try:
        process_job_description()
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        console.print("\n\nOperation cancelled by user", style="yellow")
    except Exception as e:
        logger.error(f"Critical error: {str(e)}", exc_info=True)
        console.print(f"\n❌ An error occurred: {str(e)}", style="bold red")

if __name__ == "__main__":
    main() 