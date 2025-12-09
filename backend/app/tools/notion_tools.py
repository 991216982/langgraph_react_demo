from langchain_core.tools import tool

MOCK_SHOPPING_LIST = ["意面", "番茄", "罗勒", "鸡胸肉"]
MOCK_MIND_BASE = []

@tool
def get_shopping_list():
    return MOCK_SHOPPING_LIST

@tool
def add_entry_to_mindbase(entryContent: str, entryType: str):
    item = {"content": entryContent, "type": entryType}
    MOCK_MIND_BASE.append(item)
    return item

@tool
def add_to_shopping_list(data: list):
    for x in data:
        MOCK_SHOPPING_LIST.append(x)
    return {"added": data, "total": len(MOCK_SHOPPING_LIST)}

