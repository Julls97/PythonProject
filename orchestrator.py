import argparse
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from date_rules import deadline_from_phrase
from main import create_task, resolve_responsible_id, resolve_assignee_id_by_name, COMPANY_TIMEZONE
from task_parser import parse_text

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"


def preview_task(
        title: str,
        description: str,
        assignee_id: int | None,
        deadline: datetime,
) -> None:
    print()
    print("--- Предпросмотр задачи ---")
    print(f"Название: {title}")
    print(f"Описание: {description}")
    print(f"Ответственный ID: {assignee_id}")
    print(f"Дедлайн: {deadline.isoformat()}")


def process_text(user_text: str) -> None:
    extraction = parse_text(user_text)

    now = datetime.now(COMPANY_TIMEZONE)

    if not extraction.tasks:
        print("В сообщении не найдено задач.")
        return

    for task in extraction.tasks:
        assignee_id = resolve_assignee_id_by_name(task.assignee_name)
        responsible_id = resolve_responsible_id(assignee_id)
        deadline = deadline_from_phrase(task.due_phrase, now)

        preview_task(
            title=task.title,
            description=task.description,
            assignee_id=responsible_id,
            deadline=deadline,
        )

        if not DRY_RUN:
            create_task(
                title=task.title,
                description=task.description,
                assignee_id=responsible_id,
                deadline=deadline,
            )


if __name__ == "__main__":
    creator_id = 1
    text = (
        #"Алексей Иванов, подготовь отчёт"
         "Смирнов, подготовь отчёт"
        # "Скажи Алексею Иванову, чтобы к пятнице накидал план статьи про маркетинг, а Петров пусть проверит баг на главной странице как можно быстрее."
    )

    parser = argparse.ArgumentParser(
        description="Создание задач Bitrix24 из свободного текста"
    )

    parser.add_argument(
        "--text",
        # required=True,
        help="Исходный текст",
        default=text,
    )

    parser.add_argument(
        "--creator-id",
        # required=True,
        type=int,
        help="ID отправителя и постановщика задач",
        default=creator_id,
    )

    args = parser.parse_args()

    process_text(args.text)