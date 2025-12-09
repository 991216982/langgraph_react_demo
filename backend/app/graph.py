"""构建并编译 LangGraph 图，将监督节点与各子智能体连接起来。"""

from langgraph.graph import MessagesState, StateGraph, START, END
from .agents.supervisor import supervisor_node
from .utils.factory import create_agent_node
from .config import MEMBERS


class State(MessagesState):
    """消息状态容器，继承自 `MessagesState`。"""
    pass


builder = StateGraph(State)
# 从起点进入监督节点，由监督节点决定路由到具体子智能体
builder.add_edge(START, "supervisor")
builder.add_node("supervisor", supervisor_node)
# 为每个成员添加对应的节点与执行函数
for member in MEMBERS:
    builder.add_node(member, create_agent_node(member))
# 编译图并命名，便于调试与可视化
graph = builder.compile()
graph.name = "Demo Home Assistant"
