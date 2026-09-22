"""
rag_chain.py — An LCEL chain: retriever → prompt → model → parser.

Loads the persisted FAISS index and exposes `rag_chain` which accepts
{"question": "..."} and returns a string answer grounded in company
documents.
"""

from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.config import embeddings, llm
from src.prompts import RAG_PROMPT

# ── Load persisted FAISS index ────────────────────────────────────────
INDEX_DIR = Path(__file__).resolve().parent.parent / "vectorstore"


def get_retriever(k: int = 4):
    """Return a FAISS retriever from the saved index."""
    vectorstore = FAISS.load_local(
        str(INDEX_DIR),
        embeddings,
        allow_dangerous_deserialization=True,   # required for pickle-based index
    )
    return vectorstore.as_retriever(search_kwargs={"k": k})


def format_docs(docs) -> str:
    """Join retrieved document contents into a single context string."""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


# ── LCEL RAG chain ────────────────────────────────────────────────────
# Pipe: question → (retrieve + passthrough) → prompt → llm → parse
def build_rag_chain():
    """Build and return the RAG LCEL chain."""
    retriever = get_retriever()
    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )
    return chain


rag_chain = build_rag_chain()
