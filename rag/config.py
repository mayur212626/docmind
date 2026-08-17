import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

# where the persisted vector store lives
CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma_db")
COLLECTION = "documents"

# retrieval settings
TOP_K = 4
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

# if the best match scores below this, we treat it as "no good answer"
MIN_SCORE = 0.35
