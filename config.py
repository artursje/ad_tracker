import os
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_config():
    """Load configuration from config.yaml file"""
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Override with environment variables if available
    if 'EMAIL_PASSWORD' in os.environ:
        config['email']['password'] = os.environ['EMAIL_PASSWORD']
    
    return config 