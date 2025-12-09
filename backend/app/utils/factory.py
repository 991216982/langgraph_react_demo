"""智能体工厂：根据配置构建子智能体节点函数。"""

import logging
from typing import Literal
import os
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import AIMessage
from langgraph.types import Command
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from ..config import AGENTS
from ..tools.registry import TOOLS_REGISTRY
logger = logging.getLogger(__name__)

def _parse_tool_name(tool_description: str) -> str:
    """从工具描述字符串中解析函数名。"""
    return tool_description.split("(", 1)[0].strip()

def _get_agent_config(name: str) -> dict:
    """根据智能体名称获取模型、提示词与工具函数列表。"""
    agent_config = AGENTS[name]
    model = agent_config["model"]
    tools_desc = agent_config["tools"]
    tool_fns = []
    # 将工具描述映射为实际的函数对象
    for tool_description in tools_desc:
        tool_name = _parse_tool_name(tool_description)
        if tool_name in TOOLS_REGISTRY:
            tool_fns.append(TOOLS_REGISTRY[tool_name])
    num_tools = len(tools_desc)
    tools_list = "\n".join(f"   - {tool}" for tool in tools_desc)
    prompt = agent_config["prompt"].format(num_tools=num_tools, tools_list=tools_list)
    return {"model": model, "prompt": prompt, "tools": tool_fns}

def create_agent_node(agent_name: str, default_goto: str = "supervisor"):
    """创建指定智能体的节点函数。

    参数:
        agent_name: 智能体名称，对应配置中的键。
        default_goto: 节点执行后的默认路由目标，默认为 ``supervisor``。

    返回:
        一个可用于 `StateGraph.add_node` 的可调用节点函数。
    """
    agent_config = _get_agent_config(agent_name)
    logger.info("create_agent_node %s model=%s tools=%d", agent_name, agent_config["model"], len(agent_config["tools"]))
    dashscope_api_key = os.environ.get("DASHSCOPE_API_KEY")
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not dashscope_api_key:
        logger.error("DASHSCOPE_API_KEY 未设置")
        raise RuntimeError("DASHSCOPE_API_KEY 未设置")
    memory = MemorySaver()
    chat_model = ChatTongyi(model=agent_config["model"], model_kwargs={"enable_thinking": False})
    agent = create_react_agent(chat_model, tools=agent_config["tools"], prompt=agent_config["prompt"], checkpointer=memory)

    def node_func(state: MessagesState) -> Command[Literal[default_goto]]:
        logger.info("%s node received %d messages", agent_name, len(state["messages"]))
        result = agent.invoke(state)
        last_content = result["messages"][-1].content if result["messages"] else ""
        logger.info("%s model reply length=%d", agent_name, len(str(last_content)))
        return Command(update={"messages": [AIMessage(content=last_content, name=agent_name)]}, goto=default_goto)

    return node_func
