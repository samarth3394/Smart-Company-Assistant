# Nexora Smart Company Assistant

A support chatbot built with **LangChain**, **LangGraph**, and **Google Gemini** that combines RAG, custom tools, structured output, and an agent-driven workflow.

## Features

| Capability | Description |
|---|---|
| **RAG** | Answers questions from company HR policy and product FAQ documents using a FAISS vector store |
| **Tool calling** | Looks up live order and ticket statuses via custom `@tool` functions |
| **Structured output** | Extracts a well-formed support ticket (name, issue, priority) using Pydantic |
| **LangGraph workflow** | Routes questions through a state graph with a review/retry loop |
| **Conversation memory** | Remembers prior turns within a session via `MemorySaver` |

## Quick Start

### 1. Clone & install

```bash
cd "Smart Company Assistant"
pip install -r requirements.txt
```

### 2. Set your API key

Copy the example env file and add your [Google AI API key](https://aistudio.google.com/apikey):

```bash
cp .env.example .env
# Edit .env and paste your key
```

### 3. Ingest documents (run once)

```bash
python -m src.ingest
```

This loads `data/hr_policy.md` and `data/product_faq.md`, splits them into chunks, embeds them with Gemini, and saves a FAISS index to `vectorstore/`.

### 4. Chat!

```bash
python -m src.main
```

## Example Questions

Try these to exercise different paths:

1. **RAG path** — _"How many days of paid time off do I get after 3 years?"_
2. **Tool path** — _"What's the status of order ORD-1002?"_
3. **Ticket path** — _"I'd like to escalate an issue. My name is Alex and my CloudSync app keeps crashing."_

## Project Structure

```
smart-company-assistant/
├── .env.example          # API key placeholder
├── requirements.txt      # Python dependencies
├── data/
│   ├── hr_policy.md      # Sample HR policy document
│   └── product_faq.md    # Sample product FAQ document
├── src/
│   ├── config.py         # Loads .env, initializes Gemini LLM & embeddings
│   ├── ingest.py         # Document loading, splitting, FAISS index creation
│   ├── prompts.py        # All ChatPromptTemplate definitions
│   ├── tools.py          # @tool functions with fake in-memory data
│   ├── schemas.py        # Pydantic TicketInfo model
│   ├── rag_chain.py      # LCEL chain: retriever | prompt | model | parser
│   ├── graph.py          # LangGraph StateGraph with 5 nodes + memory
│   └── main.py           # CLI chat loop
└── README.md
```

## Tech Stack

- Python 3.10+
- LangChain + LangChain Community
- LangGraph
- Google Gemini (`gemini-2.5-flash` via `init_chat_model`)
- Google Generative AI Embeddings (`text-embedding-004`)
- FAISS (CPU)
- Pydantic v2
