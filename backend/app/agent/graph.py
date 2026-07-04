# backend/app/agent/graph.py
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from copilotkit.langgraph import copilotkit_customize_config, copilotkit_emit_state

from app.agent.state import AgentState
from app.agent.tools import (
    search_emails, start_compose, send_email,
    open_email, apply_filters, prefill_reply
)

tools = [search_emails, start_compose, send_email, open_email, apply_filters, prefill_reply]
model = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(tools)

SYSTEM_PROMPT = """You are the mail assistant for a webmail client. You control the UI directly
through tools — you don't just describe actions, you execute them via tool calls.

Rules:
- To compose: call start_compose, then stream field updates (to/subject/body).
- To search: call search_emails with parsed filters, never answer from memory.
- To open: call open_email with the matching id from the last search_results.
- To reply: use prefill_reply, which reads open_email_id from state automatically.
- Be terse in chat; let the UI do the talking.
"""

async def agent_node(state: AgentState, config):
    config = copilotkit_customize_config(config, emit_intermediate_state=[
        {"state_key": "compose_draft", "tool": "start_compose"},
        {"state_key": "search_results", "tool": "search_emails"},
    ])
    response = await model.ainvoke(
        [{"role": "system", "content": SYSTEM_PROMPT}, *state["messages"]],
        config
    )
    await copilotkit_emit_state(config, state)
    return {"messages": [response]}

def route(state: AgentState):
    last = state["messages"][-1]
    return "tools" if getattr(last, "tool_calls", None) else END

graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", route, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")

compiled_graph = graph.compile()