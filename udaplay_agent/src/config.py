import os
import warnings
from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Auto-correct if keys are clearly swapped in .env
if (
	OPENAI_API_KEY
	and TAVILY_API_KEY
	and OPENAI_API_KEY.startswith("tvly-")
	and (TAVILY_API_KEY.startswith("sk-") or TAVILY_API_KEY.startswith("sk-proj-"))
):
	OPENAI_API_KEY, TAVILY_API_KEY = TAVILY_API_KEY, OPENAI_API_KEY
	warnings.warn(
		"OPENAI_API_KEY and TAVILY_API_KEY appeared swapped in .env; using corrected values at runtime."
	)

OPENAI_ENABLED = bool(OPENAI_API_KEY) and (
	OPENAI_API_KEY.startswith("sk-") or OPENAI_API_KEY.startswith("sk-proj-")
)
TAVILY_ENABLED = bool(TAVILY_API_KEY) and TAVILY_API_KEY.startswith("tvly-")

if not OPENAI_ENABLED:
	warnings.warn(
		"OPENAI_API_KEY is missing or invalid. Running in offline fallback mode for evaluation/reporting/embeddings."
	)

if not TAVILY_ENABLED:
	warnings.warn(
		"TAVILY_API_KEY is missing or invalid. Web search fallback is disabled."
	)

openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_ENABLED else None
tavily_client = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_ENABLED else None

EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
