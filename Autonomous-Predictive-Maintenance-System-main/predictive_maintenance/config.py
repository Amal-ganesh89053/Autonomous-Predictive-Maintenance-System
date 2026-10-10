import os
import dotenv

import itertools
from google.genai import Client
from google.adk.models.google_llm import Gemini

dotenv.load_dotenv()

# Model Configuration
HEAVY_MODEL_NAME = os.getenv("HEAVY_MODEL", "gemini-2.5-flash")

_heavy_models = []
key1 = os.getenv("GOOGLE_API_KEY1")
key2 = os.getenv("GOOGLE_API_KEY2")

if key1:
    m1 = Gemini(model=HEAVY_MODEL_NAME)
    m1.api_client = Client(api_key=key1)
    _heavy_models.append(m1)

if key2:
    m2 = Gemini(model=HEAVY_MODEL_NAME)
    m2.api_client = Client(api_key=key2)
    _heavy_models.append(m2)

if not _heavy_models:
    _heavy_models.append(Gemini(model=HEAVY_MODEL_NAME))

_model_cycle = itertools.cycle(_heavy_models)

def get_heavy_model():
    """Returns a heavy model instance, round-robining across available API keys to avoid rate limits."""
    return next(_model_cycle)

# Lite: For simple tasks (OpenRouter)
LITE_MODEL = os.getenv("LITE_MODEL", "openai/nex-agi/deepseek-v3.1-nex-n1:free")
