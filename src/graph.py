"""
graph.py — The LangGraph StateGraph that orchestrates the entire workflow.

Nodes:
  router       → LLM classifies the question into rag / tool / ticket
  rag_node     → answers from FAISS-backed company documents (LCEL chain)
  tool_node    → binds tools to the LLM so it can call order/ticket lookups
  ticket_node  → extracts a TicketInfo via with_structured_output
  review_node  → quality gate: loops back once if the answer is weak/empty

Edges:
  START → router → (conditional) → rag_node / tool_node / ticket_node
  rag_node / tool_node / ticket_node → review_node
  review_node → (conditional) → router (retry once) or END

Memory:
  MemorySaver checkpointer keeps conversation history across turns
  within the same thread_id.
"""

from __future__ import annotations

from typing import TypedDict, Annotated, Literal

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from src.config import llm
from src.prompts import ROUTER_PROMPT, TOOL_SYSTEM_PROMPT, TICKET_PROMPT
from src.rag_chain import rag_chain
from src.tools import all_tools
from src.schemas import TicketInfo


# ══════════════════════════════════════════════════════════════════════
#  State definition
# ══════════════════════════════════════════════════════════════════════

class State(TypedDict):
    """Graph state that flows between nodes."""
    messages: Annotated[list, add_messages]   # conversation history
    question: str                              # current user question
    route: str                                 # router decision
    answer: str                                # produced answer
    retry_count: int                           # review-loop counter


# ══════════════════════════════════════════════════════════════════════
#  Node implementations
# ══════════════════════════════════════════════════════════════════════

def router_node(state: State) -> dict:
    """Classify the user question into rag / tool / ticket."""
    question = state["question"]
    chain = ROUTER_PROMPT | llm
    result = chain.invoke({"question": question})
    route = result.content.strip().lower()
    # Normalise to one of the three known routes
    if route not in ("rag", "tool", "ticket"):
        route = "rag"  # default fallback
    return {"route": route}


def rag_node(state: State) -> dict:
    """Answer the question from company documents via the RAG chain."""
    question = state["question"]
    answer = rag_chain.invoke(question)
    return {
        "answer": answer,
        "messages": [AIMessage(content=answer)],
    }


def tool_node(state: State) -> dict:
    """Bind tools to the LLM, let it call get_order_status / get_ticket_status,
    and return the final answer."""
    question = state["question"]
    llm_with_tools = llm.bind_tools(all_tools)

    # First call: the model may produce a tool-call message
    messages = [
        SystemMessage(content=TOOL_SYSTEM_PROMPT),
        HumanMessage(content=question),
    ]
    ai_msg = llm_with_tools.invoke(messages)
    messages.append(ai_msg)

    # If the model requested tool calls, execute them
    if ai_msg.tool_calls:
        tool_map = {t.name: t for t in all_tools}
        for tc in ai_msg.tool_calls:
            tool_fn = tool_map.get(tc["name"])
            if tool_fn:
                tool_result = tool_fn.invoke(tc["args"])
                from langchain_core.messages import ToolMessage
                messages.append(
                    ToolMessage(content=str(tool_result), tool_call_id=tc["id"])
                )

        # Second call: model summarises the tool results for the user
        final_msg = llm_with_tools.invoke(messages)
        answer = final_msg.content
    else:
        answer = ai_msg.content

    return {
        "answer": answer,
        "messages": [AIMessage(content=answer)],
    }


def ticket_node(state: State) -> dict:
    """Extract a structured TicketInfo from the conversation and
    'save' it (printed to console as a demo)."""
    # Build a text summary of the conversation for extraction
    conversation_text = "\n".join(
        f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
        for m in state.get("messages", [])
        if isinstance(m, (HumanMessage, AIMessage))
    )
    # Add the current question if not already in messages
    if state["question"] not in conversation_text:
        conversation_text += f"\nUser: {state['question']}"

    structured_llm = llm.with_structured_output(TicketInfo)
    ticket: TicketInfo = structured_llm.invoke(
        TICKET_PROMPT.format_messages(conversation=conversation_text)
    )

    # "Save" the ticket (in a real app this would go to a database)
    ticket_summary = (
        f"📋 Support ticket created!\n"
        f"   Name     : {ticket.name}\n"
        f"   Issue    : {ticket.issue}\n"
        f"   Priority : {ticket.priority}"
    )
    answer = (
        f"I've created a support ticket for you:\n\n{ticket_summary}\n\n"
        f"A human agent will follow up shortly."
    )
    return {
        "answer": answer,
        "messages": [AIMessage(content=answer)],
    }


def review_node(state: State) -> dict:
    """Quality gate: check if the answer is non-empty and reasonably
    long.  If not, allow one retry before falling back."""
    answer = state.get("answer", "")
    retry_count = state.get("retry_count", 0)

    is_weak = (not answer) or len(answer.strip()) < 30

    if is_weak and retry_count < 1:
        return {"retry_count": retry_count + 1}

    if is_weak:
        fallback = (
            "I'm sorry, I wasn't able to find a good answer to your question. "
            "Would you like me to create a support ticket so a human agent "
            "can help you?"
        )
        return {
            "answer": fallback,
            "messages": [AIMessage(content=fallback)],
            "retry_count": retry_count,
        }

    return {"retry_count": retry_count}


# ══════════════════════════════════════════════════════════════════════
#  Routing functions (used by add_conditional_edges)
# ══════════════════════════════════════════════════════════════════════

def route_after_router(state: State) -> Literal["rag_node", "tool_node", "ticket_node"]:
    """Pick the next node based on the router's classification."""
    route = state.get("route", "rag")
    mapping = {
        "rag": "rag_node",
        "tool": "tool_node",
        "ticket": "ticket_node",
    }
    return mapping.get(route, "rag_node")


def route_after_review(state: State) -> Literal["router_node", "__end__"]:
    """If the review flagged a retry and we haven't exhausted retries,
    loop back to the router; otherwise finish."""
    answer = state.get("answer", "")
    retry_count = state.get("retry_count", 0)
    is_weak = (not answer) or len(answer.strip()) < 30
    if is_weak and retry_count <= 1:
        return "router_node"
    return END


# ══════════════════════════════════════════════════════════════════════
#  Build the graph
# ══════════════════════════════════════════════════════════════════════

def build_graph():
    """Construct and compile the LangGraph StateGraph."""
    builder = StateGraph(State)

    # ── Add nodes ─────────────────────────────────────────────────────
    builder.add_node("router_node", router_node)
    builder.add_node("rag_node", rag_node)
    builder.add_node("tool_node", tool_node)
    builder.add_node("ticket_node", ticket_node)
    builder.add_node("review_node", review_node)

    # ── Edges ─────────────────────────────────────────────────────────
    builder.add_edge(START, "router_node")

    builder.add_conditional_edges(
        "router_node",
        route_after_router,
        {
            "rag_node": "rag_node",
            "tool_node": "tool_node",
            "ticket_node": "ticket_node",
        },
    )

    builder.add_edge("rag_node", "review_node")
    builder.add_edge("tool_node", "review_node")
    builder.add_edge("ticket_node", "review_node")

    builder.add_conditional_edges(
        "review_node",
        route_after_review,
        {
            "router_node": "router_node",
            END: END,
        },
    )

    # ── Compile with memory ───────────────────────────────────────────
    checkpointer = MemorySaver()
    graph = builder.compile(checkpointer=checkpointer)

    return graph


# Pre-built graph instance
app = build_graph()
