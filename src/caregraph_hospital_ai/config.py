
import os
from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "local")
APP_NAME = os.getenv("APP_NAME", "CareGraph Hospital AI")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

