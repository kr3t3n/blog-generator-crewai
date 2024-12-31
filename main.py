import os
from termcolor import colored
import yaml
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from crew import ContentCreationCrew
from models.content_models import ContentOutput
import re
import copy

# Constants
SUBJECT = "What is the best AI model in each category?"
OUTPUT_DIR = "output"

def sanitize_filename(name: str) -> str:
    """Convert a string into a valid filename."""
    # Replace any character that's not alphanumeric, space, or underscore with underscore
    sanitized = re.sub(r'[^\w\s-]', '_', name)
    # Replace multiple spaces or underscores with a single underscore
    sanitized = re.sub(r'[\s_]+', '_', sanitized)
    # Trim underscores from start and end and convert to lowercase
    return sanitized.strip('_').lower()

def sanitize_folder_name(name: str) -> str:
    """Convert a string into a valid folder name."""
    # Replace any character that's not alphanumeric, space, or underscore with underscore
    sanitized = re.sub(r'[^\w\s-]', '_', name)
    # Replace multiple spaces or underscores with a single underscore
    sanitized = re.sub(r'[\s_]+', '_', sanitized)
    # Trim underscores from start and end
    return sanitized.strip('_')

def load_yaml_config(file_path: str) -> dict:
    """Load YAML configuration file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            
            # Create a deep copy to avoid modifying the original
            config = copy.deepcopy(config)
            
            # Replace {subject} placeholders in the configuration
            for key, value in config.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        if isinstance(subvalue, str):
                            config[key][subkey] = subvalue.replace('{subject}', SUBJECT)
                elif isinstance(value, str):
                    config[key] = value.replace('{subject}', SUBJECT)
            
            return config
    except Exception as e:
        print(colored(f"Error loading YAML file {file_path}: {str(e)}", "red"))
        raise

def save_output(result, filename_prefix: str = None):
    """Save the content output to files."""
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a subfolder with subject and timestamp
        subfolder_name = f"{sanitize_folder_name(SUBJECT)}_{timestamp}"
        subfolder_path = os.path.join(OUTPUT_DIR, subfolder_name)
        os.makedirs(subfolder_path, exist_ok=True)
        print(colored(f"Created output folder: {subfolder_path}", "cyan"))
        
        # Use sanitized subject as filename prefix if none provided
        if filename_prefix is None:
            filename_prefix = sanitize_filename(SUBJECT)
        
        # Handle different result types
        if hasattr(result, 'raw'):  # CrewOutput object
            try:
                output = ContentOutput(**result.raw)
            except Exception as e:
                print(colored(f"Error parsing CrewOutput: {str(e)}", "red"))
                if isinstance(result.raw, str):
                    # If raw output is a string, try to save it directly
                    article_path = os.path.join(subfolder_path, f"{filename_prefix}_article.md")
                    with open(article_path, "w", encoding="utf-8") as f:
                        f.write(result.raw)
                    print(colored(f"Raw output saved to {article_path}", "green"))
                    return
                raise
        elif isinstance(result, dict):
            output = ContentOutput(**result)
        else:
            output = result
        
        # Save article
        article_path = os.path.join(subfolder_path, f"{filename_prefix}_article.md")
        with open(article_path, "w", encoding="utf-8") as f:
            f.write(output.article)
        print(colored(f"Article saved to {article_path}", "green"))
        
        # Save social media posts
        social_path = os.path.join(subfolder_path, f"{filename_prefix}_social.md")
        with open(social_path, "w", encoding="utf-8") as f:
            for post in output.social_media_posts:
                f.write(f"## {post.platform}\n\n{post.content}\n\n---\n\n")
        print(colored(f"Social media posts saved to {social_path}", "green"))
    except Exception as e:
        print(colored(f"Error saving output: {str(e)}", "red"))
        print(colored(f"Result type: {type(result)}", "yellow"))
        if hasattr(result, 'raw'):
            print(colored(f"Raw output type: {type(result.raw)}", "yellow"))
            print(colored(f"Raw output: {result.raw}", "yellow"))
        raise

def main():
    print(colored("Loading environment variables...", "cyan"))
    load_dotenv()

    print(colored(f"Using subject: {SUBJECT}", "cyan"))
    print(colored("Loading configurations...", "cyan"))
    agents_config = load_yaml_config('config/agents.yaml')
    tasks_config = load_yaml_config('config/tasks.yaml')

    print(colored("Setting up LLM...", "cyan"))
    llm = ChatOpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com/v1",
        model_name="deepseek/deepseek-chat",
        temperature=0.7
    )

    print(colored("Creating crew...", "cyan"))
    content_crew = ContentCreationCrew(
        agents_config=agents_config,
        tasks_config=tasks_config,
        llm=llm
    )

    print(colored("Starting content creation process...", "cyan"))
    try:
        result = content_crew.kickoff()
        print(colored("Content creation completed successfully!", "green"))
        save_output(result)  # Let it use the subject as filename prefix
    except Exception as e:
        print(colored("Error: Content creation process failed", "red"))
        print(colored(f"Error details: {str(e)}", "red"))

if __name__ == "__main__":
    main() 