"""Notion 工具（内存模拟）：管理购物清单与 Mind Base。"""

from langchain_core.tools import tool

MOCK_SHOPPING_LIST = ["意面", "番茄", "罗勒", "鸡胸肉"]
MOCK_MIND_BASE = []

@tool
def get_shopping_list():
    """获取未完成的购物清单。"""
    return MOCK_SHOPPING_LIST

@tool
def add_entry_to_mindbase(entryContent: str, entryType: str):
    """向 Mind Base 添加一条记录。"""
    item = {"content": entryContent, "type": entryType}
    MOCK_MIND_BASE.append(item)
    return item

@tool
def add_to_shopping_list(data: list):
    """批量添加购物项。"""
    for item in data:
        MOCK_SHOPPING_LIST.append(item)
    return {"added": data, "total": len(MOCK_SHOPPING_LIST)}
