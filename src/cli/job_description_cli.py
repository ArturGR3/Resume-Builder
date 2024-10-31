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

from src.data_extraction.data_extraction_job_description import main as extract_job_description
from src.data_extraction.data_extraction_resume import main as extract_resume

console = Console()

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
    """Process a file based on its extension. Returns the path to the saved JSON."""
    if not os.path.exists(file_path):
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
    """Process a resume file based on its extension. Returns the path to the saved JSON."""
    if not os.path.exists(file_path):
        console.print("❌ File not found!", style="bold red")
        return None
    
    _, file_extension = os.path.splitext(file_path)
    
    if file_extension.lower() == '.json':
        # Handle JSON file
        try:
            with open(file_path, 'r') as f:
                json_data = json.load(f)
            
            resume_dir = Path('/home/artur/github/personal/Resume-Builder/resumes')
            resume_dir.mkdir(parents=True, exist_ok=True)
            
            json_path = resume_dir / f"resume_{date.today().strftime('%Y-%m-%d')}.json"
            with open(json_path, 'w') as f:
                json.dump(json_data, f, indent=2)
            
            return str(json_path)
            
        except json.JSONDecodeError:
            console.print("❌ Invalid JSON format in file!", style="bold red")
            return None
    
    elif file_extension.lower() in ['.md', '.pdf']:
        # Process through AI
        return extract_resume(file_path)
    
    else:
        console.print(f"❌ Unsupported file type: {file_extension}", style="bold red")
        return None

def process_resume():
    console.print(Panel.fit("\nResume Processing", style="bold blue"))
    
    resume_input = Prompt.ask(
        "How would you like to provide the resume?",
        choices=["text", "file"],
        default="file"
    )
    
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

def process_job_description():
    console.print(Panel.fit("Job Description Processor", style="bold blue"))
    
    input_method = Prompt.ask(
        "How would you like to provide the job description?",
        choices=["text", "file"],
        default="text"
    )
    
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
                json_path = extract_job_description(temp_path)
                console.print(f"\n✅ Job description processed and saved to: [bold green]{json_path}[/]")
            finally:
                status.update("[bold yellow]Cleaning up temporary files...")
                os.unlink(temp_path)
    
    else:  # file
        file_path = Prompt.ask("Enter the path to the job description file")
        
        with Status("[bold yellow]Processing file...", spinner="dots") as status:
            json_path = process_file(file_path)
            if json_path:
                console.print(f"\n✅ Job description processed and saved to: [bold green]{json_path}[/]")
    
    if json_path and Confirm.ask("\nWould you like to process a resume now?"):
        process_resume()

def main():
    try:
        process_job_description()
    except KeyboardInterrupt:
        console.print("\n\nOperation cancelled by user", style="yellow")
    except Exception as e:
        console.print(f"\n❌ An error occurred: {str(e)}", style="bold red")

if __name__ == "__main__":
    main() 