"""工具注册表：将工具函数统一映射为名称，供智能体调用。"""

from .calendar_tools import get_current_date_and_time, get_calendar_events, add_calendar_event, create_calendar
from .notion_tools import get_shopping_list, add_entry_to_mindbase, add_to_shopping_list
from .meal_tools import get_recipes

TOOLS_REGISTRY = {
  "get_current_date_and_time": get_current_date_and_time,
  "get_calendar_events": get_calendar_events,
  "add_calendar_event": add_calendar_event,
  "create_calendar": create_calendar,
  "get_shopping_list": get_shopping_list,
  "add_entry_to_mindbase": add_entry_to_mindbase,
  "add_to_shopping_list": add_to_shopping_list,
  "get_recipes": get_recipes,
}
