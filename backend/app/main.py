"""FastAPI 应用入口，提供智能体调用接口与图可视化等端点。"""

import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from .graph import graph
from .config import MEMBERS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    stream=sys.stdout  # 明确指定输出到 stdout

)
logger = logging.getLogger(__name__)
app = FastAPI()

# 配置跨域，允许本地开发前端与任意来源访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS: Dict[str, list] = {}

class InvokeInput(BaseModel):
    """调用输入模型，封装待处理的消息列表。"""
    session_id: Optional[str] = None
    messages: list
    recursion_limit: Optional[int] = None

@app.get("/")
def root():
    """健康检查端点，返回服务运行状态。"""
    logger.info("根路径健康检查")
    return {"status": "ok"}

@app.get("/api/agents")
def list_agents():
    """返回已注册的子智能体名称列表。"""
    logger.info("列出智能体数量=%d", len(MEMBERS))
    return {"agents": MEMBERS}

@app.get("/api/mermaid")
def mermaid():
    """返回当前 LangGraph 的 Mermaid 表示，用于前端可视化。"""
    mermaid_text = graph.get_graph().draw_mermaid()
    logger.info("请求Mermaid图，长度=%d", len(mermaid_text))
    return {"mermaid": mermaid_text}

@app.post("/api/invoke")
def invoke(input: InvokeInput):
    """执行消息流并返回归一化后的消息列表。

    参数:
        input: `InvokeInput`，包含要提交到图的消息列表。

    返回:
        一个包含消息类型与内容的列表，用于前端展示。
    """
    def to_role_dict_list(items: List[Any]) -> List[Dict[str, Any]]:
        result = []
        for it in items:
            if isinstance(it, dict) and "role" in it and "content" in it:
                result.append({"role": it["role"], "content": it["content"]})
            elif isinstance(it, (list, tuple)) and len(it) >= 2:
                result.append({"role": it[0], "content": it[1]})
            else:
                role = getattr(it, "type", "user")
                content = getattr(it, "content", str(it))
                role_map = {"human": "user", "ai": "assistant"}
                result.append({"role": role_map.get(role, role), "content": content})
        return result

    session_id = input.session_id or "default"
    prev = SESSIONS.get(session_id, [])
    new_msgs = to_role_dict_list(input.messages)
    merged = prev + new_msgs
    head_in = (new_msgs[0]["content"][:200] if new_msgs else "")
    tail_prev = (prev[-1]["content"][:200] if prev else "")
    logger.info("调用会话=%s 历史消息=%d 新消息=%d 新消息头=%s 历史尾=%s", session_id, len(prev), len(input.messages), head_in, tail_prev)
    cfg = {"recursion_limit": input.recursion_limit or 20}
    logger.info("调用配置 递归限制=%d", cfg["recursion_limit"])
    state = graph.invoke({"messages": merged}, cfg)
    normalized = [(message.type, getattr(message, "content", "")) for message in state["messages"]]
    # store as role dicts for next round
    role_map = {"human": "user", "ai": "assistant"}
    stored = [{"role": role_map.get(m.type, m.type), "content": getattr(m, "content", "")} for m in state["messages"]]
    SESSIONS[session_id] = stored
    out_head = (normalized[0][1][:200] if normalized else "")
    out_tail = (normalized[-1][1][:200] if normalized else "")
    logger.info("调用完成 会话=%s 总消息数=%d 输出头=%s 输出尾=%s", session_id, len(normalized), out_head, out_tail)
    return {"messages": normalized, "session_id": session_id}
