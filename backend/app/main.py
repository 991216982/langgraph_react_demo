"""FastAPI 应用入口，提供智能体调用接口与图可视化等端点。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .graph import graph
from .config import MEMBERS

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
    return {"status": "ok"}

@app.get("/api/agents")
def list_agents():
    """返回已注册的子智能体名称列表。"""
    return {"agents": MEMBERS}

@app.get("/api/mermaid")
def mermaid():
    """返回当前 LangGraph 的 Mermaid 表示，用于前端可视化。"""
    return {"mermaid": graph.get_graph().draw_mermaid()}

@app.post("/api/invoke")
def invoke(input: InvokeInput):
    """执行消息流并返回归一化后的消息列表。

    参数:
        input: `InvokeInput`，包含要提交到图的消息列表。

    返回:
        一个包含消息类型与内容的列表，用于前端展示。
    """
    # 将输入消息提交到图执行
    state = graph.invoke({"messages": input.messages})
    # 统一提取消息类型与文本内容
    return {"messages": [(message.type, getattr(message, "content", "")) for message in state["messages"]]}
