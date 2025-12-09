from langchain_core.tools import tool

MOCK_EMAILS = [
    {"id": "m1", "snippet": "项目更新：请查看附件", "labelIds": ["work"], "body": "本周完成了模块A的开发。"},
    {"id": "m2", "snippet": "促销活动：冬季特价", "labelIds": ["marketing"], "body": "全场八折，点击查看详情。"},
]
MOCK_SENT = []
MOCK_DRAFTS = []
MOCK_LABELS = {"work": "work", "personal": "personal", "marketing": "marketing"}

@tool
def send_email(to_email: str, subject: str, body: str):
    msg = {"to": to_email, "subject": subject, "body": body, "id": f"s{len(MOCK_SENT)+1}"}
    MOCK_SENT.append(msg)
    return msg

@tool
def check_emails(query: str = "", max_results: int = 10, only_unlabeled: bool = False):
    res = MOCK_EMAILS[:max_results]
    if only_unlabeled:
        res = [x for x in res if not x.get("labelIds")]
    return {"emails": res}

@tool
def label_email(message_id: str, label: str):
    label_id = MOCK_LABELS.get(label)
    for m in MOCK_EMAILS:
        if m["id"] == message_id and label_id:
            labs = m.get("labelIds", [])
            if label_id not in labs:
                labs.append(label_id)
            m["labelIds"] = labs
            return m
    return {"error": "message or label not found"}

@tool
def create_draft(to_email: str, subject: str, body: str):
    d = {"to": to_email, "subject": subject, "body": body, "id": f"d{len(MOCK_DRAFTS)+1}"}
    MOCK_DRAFTS.append(d)
    return d

