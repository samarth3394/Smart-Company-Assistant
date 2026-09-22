"""
schemas.py — Pydantic models for structured output.

TicketInfo is used by the ticket_node to extract a well-formed support
ticket from the conversation, demonstrating LangChain's
`with_structured_output` capability.
"""

from pydantic import BaseModel, Field


class TicketInfo(BaseModel):
    """A structured support ticket created when the assistant cannot
    resolve the user's issue or the user explicitly asks to escalate."""

    name: str = Field(
        description="Full name of the customer or 'Unknown' if not provided."
    )
    issue: str = Field(
        description="A concise summary of the customer's problem or request."
    )
    priority: str = Field(
        description="Ticket priority: 'low', 'medium', 'high', or 'critical'."
    )
