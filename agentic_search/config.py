import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
LANGSMITH_API_KEY = os.environ.get("LANGSMITH_API_KEY", "")
# (Stub) Google API keys, not used in stub functions
GOOGLE_PLACES_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")
GOOGLE_DIRECTIONS_API_KEY = os.environ.get("GOOGLE_DIRECTIONS_API_KEY", "")
