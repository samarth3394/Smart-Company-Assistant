"""
main.py — CLI chat loop that drives the LangGraph agent.

Keeps a persistent thread_id so conversation memory carries across
turns.  Type 'quit' or 'exit' to stop.

Run with:
    python -m src.main
"""

import sys
import os
import uuid

# Fix Windows console encoding for emoji/unicode output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from langchain_core.messages import HumanMessage
from src.graph import app


def main():
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print("=" * 56)
    print("  Nexora Smart Company Assistant")
    print("  Type your question below.  'quit' or 'exit' to stop.")
    print("=" * 56)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        # Build the initial state for this turn
        state_input = {
            "messages": [HumanMessage(content=user_input)],
            "question": user_input,
            "answer": "",
            "route": "",
            "retry_count": 0,
        }

        # Run the graph
        result = app.invoke(state_input, config=config)

        answer = result.get("answer", "I'm sorry, something went wrong.")
        print(f"\nAssistant: {answer}")


if __name__ == "__main__":
    main()
