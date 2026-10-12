# Задачи Bitrix24

Создание задач из свободного текста через Python и OpenClaw.

## Установка

```powershell
python -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Заполните `.env`. 
Для проверки используйте **`DRY_RUN=true`**.

## Запуск

Из корня проекта:

```powershell
& '.\.venv\Scripts\python.exe' '.\orchestrator.py' --text 'Подготовить план статьи к пятнице.' --creator-id 1
```

Замените `1` на ID постановщика в Bitrix24.
Для создания задач установите `DRY_RUN=false`.

## OpenClaw

Skill: `skills/bitrix-tasks/SKILL.md`.
Корень проекта: `{baseDir}\..\..`.

Не передавайте `.env` с секретами.
Не повторяйте запуск автоматически при неизвестном результате.