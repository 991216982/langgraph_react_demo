from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langgraph.types import Command
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from ..config import AGENTS
from ..tools.registry import TOOLS_REGISTRY

def _parse_tool_name(s: str) -> str:
    return s.split("(", 1)[0].strip()

def _get_agent_config(name: str) -> dict:
    cfg = AGENTS[name]
    model = cfg["model"]
    tools_desc = cfg["tools"]
    tool_fns = []
    for t in tools_desc:
        n = _parse_tool_name(t)
        if n in TOOLS_REGISTRY:
            tool_fns.append(TOOLS_REGISTRY[n])
    num_tools = len(tools_desc)
    tools_list = "\n".join(f"   - {t}" for t in tools_desc)
    prompt = cfg["prompt"].format(num_tools=num_tools, tools_list=tools_list)
    return {"model": model, "prompt": prompt, "tools": tool_fns}

def create_agent_node(agent_name: str, default_goto: str = "supervisor"):
    agent_cfg = _get_agent_config(agent_name)
    memory = MemorySaver()
    llm = ChatOpenAI(model=agent_cfg["model"])
    agent = create_react_agent(llm, tools=agent_cfg["tools"], prompt=agent_cfg["prompt"], checkpointer=memory)
    def node_func(state: MessagesState) -> Command[Literal[default_goto]]:
        result = agent.invoke(state)
        return Command(update={"messages": [AIMessage(content=result["messages"][-1].content, name=agent_name)]}, goto=default_goto)
    return node_func

