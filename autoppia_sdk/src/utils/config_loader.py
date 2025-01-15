import os
import yaml
from typing import Dict, Any

def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration from YAML file or environment variables."""
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
    else:
        # Fallback to environment variables
        config = {
            "email_agent": {
                "model": os.getenv("OPENAI_MODEL", "gpt-4"),
                "instruction": os.getenv("EMAIL_INSTRUCTION", "You are an email assistant that can help compose and send emails."),
                "smtp": {
                    "server": os.getenv("SMTP_SERVER"),
                    "port": int(os.getenv("SMTP_PORT", "587")),
                },
                "imap": {
                    "server": os.getenv("IMAP_SERVER"),
                    "port": int(os.getenv("IMAP_PORT", "993")),
                },
                "credentials": {
                    "email": os.getenv("EMAIL"),
                    "password": os.getenv("PASSWORD"),
                }
            }
        }
    return config 