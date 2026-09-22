"""
config.py — Loads environment variables and initializes the Gemini LLM
and embedding models. Every other module imports from here to get a
pre-configured model instance.
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# ── Load .env ─────────────────────────────────────────────────────────
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise EnvironmentError(
        "GOOGLE_API_KEY is not set. Copy .env.example to .env and add your key."
    )

# ── LLM (Gemini chat model via the universal init_chat_model helper) ──
#    Change the model string here if a newer Gemini version is available.
llm = init_chat_model(
    "google_genai:gemini-2.5-flash",
    temperature=0.3,
)

# ── Embeddings (Google Generative AI embeddings for the vector store) ──
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
)
