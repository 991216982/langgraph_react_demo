"""FastAPI 应用入口，提供智能体调用接口与图可视化等端点。"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .graph import graph
from .config import MEMBERS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
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

class InvokeInput(BaseModel):
    """调用输入模型，封装待处理的消息列表。"""

    messages: list

@app.get("/")
def root():
    """健康检查端点，返回服务运行状态。"""
    logger.info("root health check")
    return {"status": "ok"}

@app.get("/api/agents")
def list_agents():
    """返回已注册的子智能体名称列表。"""
    logger.info("list agents: %d", len(MEMBERS))
    return {"agents": MEMBERS}

@app.get("/api/mermaid")
def mermaid():
    """返回当前 LangGraph 的 Mermaid 表示，用于前端可视化。"""
    mermaid_text = graph.get_graph().draw_mermaid()
    logger.info("mermaid requested, length=%d", len(mermaid_text))
    return {"mermaid": mermaid_text}

@app.post("/api/invoke")
def invoke(input: InvokeInput):
    """执行消息流并返回归一化后的消息列表。

    参数:
        input: `InvokeInput`，包含要提交到图的消息列表。

    返回:
        一个包含消息类型与内容的列表，用于前端展示。
    """
    logger.info("invoke called with %d messages", len(input.messages))
    state = graph.invoke({"messages": input.messages})
    normalized = [(message.type, getattr(message, "content", "")) for message in state["messages"]]
    logger.info("invoke completed, %d messages returned", len(normalized))
    return {"messages": normalized}
