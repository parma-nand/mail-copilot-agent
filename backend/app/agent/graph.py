# backend/app/agent/graph.py
import os
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from copilotkit.langgraph import copilotkit_customize_config, copilotkit_emit_state

from app.core.config import settings
from app.agent.state import AgentState
from app.agent.tools import (
    search_emails, start_compose, send_email_tool,
    open_email, apply_filters, prefill_reply
)

os.environ["OPENAI_API_KEY"] = settings.openai_api_key

tools = [search_emails, start_compose, send_email_tool, open_email, apply_filters, prefill_reply]
model = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)

SYSTEM_PROMPT = """You are the mail assistant for a webmail client. You control the UI directly
through tools — you don't just describe actions, you execute them via tool calls.

Rules:
- To compose: call start_compose, then stream field updates (to/subject/body).
- To search: call search_emails with parsed filters, never answer from memory.
- To open: call open_email with the matching id from the last search_results.
- To reply: use prefill_reply, passing the id of the email that is currently open
  (check the conversation for the most recently opened email's id).
- Be terse in chat; let the UI do the talking.
"""

# backend/app/agent/graph.py
# backend/app/agent/graph.py
import traceback

async def agent_node(state: AgentState, config):
    print(">>> agent_node CALLED", flush=True)
    print(f">>> Incoming messages count: {len(state.get('messages', []))}", flush=True)

    config = copilotkit_customize_config(config, emit_intermediate_state=[
        {"state_key": "compose_draft", "tool": "start_compose"},
        {"state_key": "search_results", "tool": "search_emails"},
    ])

    try:
        print(">>> Calling model.ainvoke() -- about to hit OpenAI API", flush=True)
        response = await model.ainvoke(
            [{"role": "system", "content": SYSTEM_PROMPT}, *state["messages"]],
            config
        )
        print(f">>> OpenAI responded. Content: {response.content!r}", flush=True)
        print(f">>> Tool calls: {getattr(response, 'tool_calls', None)}", flush=True)

        await copilotkit_emit_state(config, state)
        print(">>> agent_node completed successfully", flush=True)
        return {"messages": [response]}
    except Exception as e:
        print(">>> AGENT NODE ERROR:", flush=True)
        traceback.print_exc()
        raise


def route(state: AgentState):
    last = state["messages"][-1]
    has_tool_calls = bool(getattr(last, "tool_calls", None))
    print(f">>> route() called — has_tool_calls={has_tool_calls}", flush=True)
    return "tools" if has_tool_calls else END

graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", route, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")

# compiled_graph = graph.compile()
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
compiled_graph = graph.compile(checkpointer=checkpointer)