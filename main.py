import datetime
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

WEBHOOK_URL = os.environ["BITRIX_WEBHOOK_URL"].rstrip("/") + "/"
DEFAULT_MANAGER_ID = int(os.environ["DEFAULT_MANAGER_ID"])
COMPANY_TIMEZONE = ZoneInfo(os.environ["COMPANY_TIMEZONE"])


def bitrix_post(method: str, payload: dict) -> dict:
    url = f"{WEBHOOK_URL}{method}"
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    request = Request(url, data=data, headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")

    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP error occurred: [{e.code}] {body}")
    except URLError as e:
        raise RuntimeError(f"Connection error: {e.reason}")


def search_user(query: str) -> list[dict]:
    result = bitrix_post("user.search",
                         {
                             "FILTER": {
                                 "FIND": query,
                             },
                             "SELECT": [
                                 "ID",
                                 "NAME",
                                 "LAST_NAME",
                                 "ACTIVE",
                             ],
                         })

    if "error" in result:
        description = result.get("description", "")
        raise RuntimeError(f"Error occurred: {description}")

    return result.get("result", [])


def resolve_assignee_id_by_name(assignee_name: str | None) -> int | None:
    if assignee_name is None:
        return None

    users = search_user(assignee_name)

    active_users = [
        user for user in users
        if str(user.get("ACTIVE", "")).lower() in ("true", "1")
    ]

    if len(active_users) == 0:
        raise RuntimeError(f"No active users found for {assignee_name}. ")

    if len(active_users) > 1:
        names = [f"{user.get("NAME", "")} {user.get("LAST_NAME", "")}".strip() for user in active_users]
        raise RuntimeError(f"Multiple active users found for {assignee_name}: {', '.join(names)}. Select with last name.")

    return active_users[0].get("ID")


def resolve_responsible_id(id: int | None) -> int | None:
    return id if str(id).isdigit() else DEFAULT_MANAGER_ID


def resolve_deadline(deadline: datetime.datetime | None) -> datetime.datetime:
    if deadline is None:
        return datetime.datetime.now(COMPANY_TIMEZONE) + datetime.timedelta(days=1)

    return deadline.astimezone(COMPANY_TIMEZONE)


def create_task(title: str, description: str, assignee_id: int | None, deadline: datetime.datetime | None,
                creator_id: int | None = None) -> int | None:
    id = resolve_assignee_id_by_name(assignee_id)
    deadline = resolve_deadline(deadline)

    payload = {
        "fields": {
            "TITLE": title,
            "DESCRIPTION": description,
            "RESPONSIBLE_ID": id,
            "CREATOR_ID": creator_id,
            "DEADLINE": deadline.isoformat()
        }
    }

    result = bitrix_post("tasks.task.add", payload)

    if "error" in result:
        raise RuntimeError(f"Error occurred: {result}")

    task = result.get("result", {}).get("task", {})
    task_id = task.get("id") or result.get("result", {}).get("id")

    print("Задача успешно создана.")
    print(f"ID задачи: {task_id}")
    print(f"Ответственный id = {id}")
    print(f"Постановщик id = {creator_id}")
    print(f"Дедлайн {deadline.isoformat()}")

    return task_id if task_id is not None else None


if __name__ == '__main__':
    users = search_user("иванов")

    for user in users:
        print(f"ID={user.get('ID')} | {user.get('NAME')} {user.get('LAST_NAME')} | ACTIVE={user.get('ACTIVE')}")