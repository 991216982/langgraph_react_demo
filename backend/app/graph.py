from langgraph.graph import MessagesState, StateGraph, START, END
from .agents.supervisor import supervisor_node
from .utils.factory import create_agent_node
from .config import MEMBERS

class State(MessagesState):
    pass

builder = StateGraph(State)
builder.add_edge(START, "supervisor")
builder.add_node("supervisor", supervisor_node)
for member in MEMBERS:
    builder.add_node(member, create_agent_node(member))
graph = builder.compile()
graph.name = "Demo Home Assistant"

