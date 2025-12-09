from langchain_core.tools import tool

MOCK_CONTACTS = [
    {"name": "张三", "email": "zhangsan@example.com"},
    {"name": "李四", "email": "lisi@example.com"},
]

@tool
def get_contacts():
    return MOCK_CONTACTS

@tool
def get_single_contact(query: str):
    for c in MOCK_CONTACTS:
        if c["name"] == query or c["email"] == query:
            return c
    return {"error": "not found"}

