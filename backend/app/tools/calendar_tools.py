"""日历工具：在内存中模拟查询与添加日历事件。"""

from datetime import datetime, timedelta
from langchain_core.tools import tool

MOCK_EVENTS = {
    "family": [
        {"summary": "家庭晚餐：意大利面", "start": {"dateTime": "2025-12-10T18:00:00+01:00"}, "end": {"dateTime": "2025-12-10T19:00:00+01:00"}, "description": "番茄酱与罗勒"},
    ],
    "personal": [
        {"summary": "健身训练", "start": {"dateTime": "2025-12-10T07:30:00+01:00"}, "end": {"dateTime": "2025-12-10T08:30:00+01:00"}, "description": "力量训练"},
    ],
    "work": [
        {"summary": "季度汇报会", "start": {"dateTime": "2025-12-11T10:00:00+01:00"}, "end": {"dateTime": "2025-12-11T11:00:00+01:00"}, "description": "准备PPT"},
    ],
}

@tool
def get_current_date_and_time():
    """获取当前日期时间与星期信息。"""
    now = datetime.now()
    return {"datetime": now.strftime("%Y-%m-%d %H:%M:%S"), "day_of_the_week": now.strftime("%A")}

@tool
def get_calendar_events(startDate: str = None, endDate: str = None):
    """返回当前内存中的所有日历事件。

    参数:
        startDate: 起始日期（保留参数，当前未过滤）。
        endDate: 结束日期（保留参数，当前未过滤）。
    """
    events = []
    for calendar_id in MOCK_EVENTS:
        for event in MOCK_EVENTS[calendar_id]:
            events.append({"calendarId": calendar_id, **event})
    return events

@tool
def add_calendar_event(startDate: datetime, endDate: datetime, calendar_name: str, title: str, description: str):
    """向指定日历添加事件，并返回创建的事件。"""
    if calendar_name not in MOCK_EVENTS:
        return {"error": "unknown calendar"}
    event = {
        "summary": title,
        "description": description,
        "start": {"dateTime": startDate.isoformat()},
        "end": {"dateTime": endDate.isoformat()},
    }
    MOCK_EVENTS[calendar_name].append(event)
    return event
