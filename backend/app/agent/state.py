# backend/app/agent/state.py
from typing import Literal, Optional
from pydantic import BaseModel, Field
from copilotkit import CopilotKitState

class EmailSummary(BaseModel):
    id: str
    sender: str
    subject: str
    preview: str
    date: str
    is_read: bool = False

class ComposeDraft(BaseModel):
    to: str = ""
    cc: str = ""
    subject: str = ""
    body: str = ""
    in_reply_to: Optional[str] = None  # email id this is replying to

class Filters(BaseModel):
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    sender: Optional[str] = None
    keyword: Optional[str] = None
    read_status: Literal["all", "read", "unread"] = "all"

class AgentState(CopilotKitState):
    """
    Single source of truth shared between LangGraph and React via CoAgents.
    Every assistant action = a mutation here. UI subscribes and re-renders.
    """
    current_view: Literal["inbox", "sent", "compose", "detail"] = "inbox"
    open_email_id: Optional[str] = None
    search_results: list[EmailSummary] = Field(default_factory=list)
    active_filters: Filters = Field(default_factory=Filters)
    compose_draft: ComposeDraft = Field(default_factory=ComposeDraft)
    last_action: Optional[str] = None  # for debugging/demo narration