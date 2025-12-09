from langchain_core.tools import tool

MOCK_RECIPES = [
    {"name": "番茄意面", "ingredients": ["意面", "番茄", "蒜", "罗勒"]},
    {"name": "鱼塔可", "ingredients": ["鱼片", "玉米饼", "卷心菜", "酸奶"]},
]

@tool
def get_recipes():
    return {"data": MOCK_RECIPES}

@tool
def human_feedback(query: str):
    return {"feedback": "已确认"}

