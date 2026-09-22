"""
tools.py — Custom tool functions backed by fake in-memory data.

The LLM reads each tool's name, docstring, and parameter schema to
decide when to invoke it.  These tools demonstrate LangChain's @tool
decorator and how to bind tools to a chat model.
"""

from langchain_core.tools import tool

# ── Fake in-memory databases ──────────────────────────────────────────

ORDERS_DB: dict[str, dict] = {
    "ORD-1001": {"status": "Shipped",     "eta": "Sep 25, 2026", "item": "CloudSync Pro License (5 seats)"},
    "ORD-1002": {"status": "Processing",  "eta": "Sep 28, 2026", "item": "CloudSync Business License (20 seats)"},
    "ORD-1003": {"status": "Delivered",    "eta": "Sep 18, 2026", "item": "CloudSync Enterprise Setup Package"},
    "ORD-1004": {"status": "Cancelled",    "eta": "N/A",          "item": "CloudSync Starter → Pro Upgrade"},
}

TICKETS_DB: dict[str, dict] = {
    "TKT-5001": {"status": "Open",       "subject": "SSO login loop on Chrome",              "assigned_to": "Riya Sharma"},
    "TKT-5002": {"status": "In Progress","subject": "Files not syncing on macOS desktop app", "assigned_to": "James Lee"},
    "TKT-5003": {"status": "Resolved",   "subject": "Billing discrepancy on Pro plan",        "assigned_to": "Priya Patel"},
    "TKT-5004": {"status": "Open",       "subject": "Request for custom API integration",     "assigned_to": "Unassigned"},
}


# ── Tool definitions ──────────────────────────────────────────────────

@tool
def get_order_status(order_id: str) -> str:
    """Look up the current status of a customer order.

    Use this tool when the user asks about an order, shipment,
    delivery, or provides an order ID like 'ORD-1001'.

    Args:
        order_id: The order identifier, e.g. 'ORD-1001'.

    Returns:
        A human-readable summary of the order status, or an error
        message if the order ID is not found.
    """
    order_id = order_id.strip().upper()
    order = ORDERS_DB.get(order_id)
    if order is None:
        return (
            f"Order '{order_id}' was not found. Please double-check the "
            f"order ID and try again. Valid format: ORD-XXXX."
        )
    return (
        f"Order {order_id}:\n"
        f"  Item   : {order['item']}\n"
        f"  Status : {order['status']}\n"
        f"  ETA    : {order['eta']}"
    )


@tool
def get_ticket_status(ticket_id: str) -> str:
    """Look up the current status of a support ticket.

    Use this tool when the user asks about an existing support ticket,
    case, or provides a ticket ID like 'TKT-5001'.

    Args:
        ticket_id: The ticket identifier, e.g. 'TKT-5001'.

    Returns:
        A human-readable summary of the ticket status, or an error
        message if the ticket ID is not found.
    """
    ticket_id = ticket_id.strip().upper()
    ticket = TICKETS_DB.get(ticket_id)
    if ticket is None:
        return (
            f"Ticket '{ticket_id}' was not found. Please double-check the "
            f"ticket ID and try again. Valid format: TKT-XXXX."
        )
    return (
        f"Ticket {ticket_id}:\n"
        f"  Subject     : {ticket['subject']}\n"
        f"  Status      : {ticket['status']}\n"
        f"  Assigned To : {ticket['assigned_to']}"
    )


# Convenience list for binding to the LLM
all_tools = [get_order_status, get_ticket_status]
