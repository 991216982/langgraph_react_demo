from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .graph import graph
from .config import MEMBERS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InvokeInput(BaseModel):
    messages: list

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/api/agents")
def list_agents():
    return {"agents": MEMBERS}

@app.get("/api/mermaid")
def mermaid():
    return {"mermaid": graph.get_graph().draw_mermaid()}

@app.post("/api/invoke")
def invoke(input: InvokeInput):
    state = graph.invoke({"messages": input.messages})
    return {"messages": [(m.type, getattr(m, "content", "")) for m in state["messages"]]}

