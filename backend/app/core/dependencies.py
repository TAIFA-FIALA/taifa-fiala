from dotenv import load_dotenv
from pathlib import Path
from .config import Settings

# Load .env file from the project root
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

settings = Settings()