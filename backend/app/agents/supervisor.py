from typing import Literal
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, END
from langgraph.types import Command
from ..config import AGENTS, MEMBERS

agent_members_prompt = []
for key, data in AGENTS.items():
    if data["name"] in MEMBERS:
        agent_members_prompt.append(f"{data['name']}: {data['description']}")
        for t in data.get("tools", []):
            agent_members_prompt.append(f"- {t}")
        agent_members_prompt.append("")
agent_members_prompt_final = "\n".join(agent_members_prompt)

supervisor_llm = ChatOpenAI(model="gpt-4o")

class State(MessagesState):
    next: str

class SupervisorOutput(TypedDict):
    next: Literal[*MEMBERS, "FINISH"]
    task_description_for_agent: str
    message_completion_summary: str

supervisor_system_prompt = f"""
# 角色
你是家用助理的监督智能体。你的职责是理解用户请求，拆解为子任务，并把每个子任务分派给最合适的子智能体，直到任务完成。

# 上下文
你可以使用以下 {len(MEMBERS)} 个子智能体：{MEMBERS}
每个子智能体的描述与工具如下：
{agent_members_prompt_final}

# 目标
分析用户请求，拆分子任务，逐步完成。为每个子任务生成清晰的中文指令并发送给对应子智能体。当全部完成时返回 next = FINISH。

# 操作指引
1. 理解用户目标。
2. 拆解为有序的子任务。
3. 为每个子任务选择最佳子智能体。
4. 下达指令时，只写该子任务需要的信息与预期输出，不提及其他智能体。
5. 评估子智能体返回是否完成该子任务，若未完成继续迭代。
6. 全部完成后，返回 FINISH。

# 重要
- 委派的任务内容写入 task_description_for_agent 字段。
- 对每次返回做出简短完成情况评估。
"""

def supervisor_node(state: State) -> Command[Literal[*MEMBERS, "__end__"]]:
    messages = [{"role": "system", "content": supervisor_system_prompt}] + state["messages"]
    response = supervisor_llm.with_structured_output(SupervisorOutput).invoke(messages)
    goto = response["next"]
    if goto == "FINISH":
        return Command(goto=END, update={"next": END})
    new_messages = [{"role": "system", "content": response["task_description_for_agent"]}]
    return Command(goto=goto, update={"next": goto, "messages": new_messages})

