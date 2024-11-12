import yaml
from pathlib import Path
from src.cli.job_description_cli import tailoring_resume_to_job_description

def load_config():
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise FileNotFoundError("config.yaml not found in root directory")
    
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    try:
        config = load_config()
        tailoring_resume_to_job_description(
            provider_for_parsing=config["job_description"]["provider"],
            model_for_parsing=config["job_description"]["model"],
            provider_for_resume=config["resume_description"]["provider"],
            model_for_resume=config["resume_description"]["model"],
            provider_for_tailoring=config["resume_tailoring"]["provider"],
            model_for_tailoring=config["resume_tailoring"]["model"]
        )
    except Exception as e:
        print(f"Error: {e}") 