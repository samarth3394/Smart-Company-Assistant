"""
ingest.py — Loads documents from data/, splits them into chunks, builds
a FAISS vector index using Gemini embeddings, and saves it to disk.

Run this script once before starting the chatbot:
    python -m src.ingest
"""

import os
import sys
from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

# Add project root to path so relative imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config import embeddings

# ── Paths ─────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
INDEX_DIR = Path(__file__).resolve().parent.parent / "vectorstore"

# ── Load documents ────────────────────────────────────────────────────
def load_documents():
    """Load all .md and .txt files from the data/ directory."""
    docs = []
    for filepath in sorted(DATA_DIR.glob("*")):
        if filepath.suffix in (".md", ".txt"):
            print(f"  Loading: {filepath.name}")
            loader = TextLoader(str(filepath), encoding="utf-8")
            docs.extend(loader.load())
    if not docs:
        print("No documents found in data/. Add .md or .txt files and re-run.")
        sys.exit(1)
    return docs

# ── Split ─────────────────────────────────────────────────────────────
def split_documents(docs):
    """Split documents into chunks suitable for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n## ", "\n### ", "\n---", "\n\n", "\n", " "],
    )
    chunks = splitter.split_documents(docs)
    print(f"  Split into {len(chunks)} chunks.")
    return chunks

# ── Build & save FAISS index ──────────────────────────────────────────
def build_index(chunks):
    """Create a FAISS index from chunks and persist it to disk."""
    print("  Building FAISS index (this calls the embedding API)...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    INDEX_DIR.mkdir(exist_ok=True)
    vectorstore.save_local(str(INDEX_DIR))
    print(f"  Index saved to {INDEX_DIR}/")
    return vectorstore


# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("Nexora Smart Assistant — Document Ingestion")
    print("=" * 50)
    docs = load_documents()
    chunks = split_documents(docs)
    build_index(chunks)
    print("Done! You can now run the chatbot with: python -m src.main")
