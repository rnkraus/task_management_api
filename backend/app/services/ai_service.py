from openai import OpenAI
from datetime import datetime, timezone
from app.core.config import settings
import json

def get_openai_client():
    if not settings.openai_api_key:
        raise RuntimeError("OpenAI API key not configured")
    return OpenAI(api_key=settings.openai_api_key)

def improve_task(title: str, description: str | None):
    client = get_openai_client()

    prompt = f"""
You are a backend assistant that improves task descriptions for a task management app.

Improve the task with these goals:
- Make the title clear, specific and concise
- Expand the description into a clear, actionable explanation
- Use professional and neutral language
- Stay close to the original intent
- Do not include any text outside JSON

Return ONLY valid JSON in this format:
{{
  "suggested_title": "...",
  "suggested_description": "..."
}}

Task:
Title: {title}
Description: {description}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.choices[0].message.content.strip()

    try:
        data = json.loads(content)

        return {
            "suggested_title": data.get("suggested_title", title),
            "suggested_description": data.get("suggested_description", description),
        }

    except Exception:
        return {
            "suggested_title": title,
            "suggested_description": description,
        }


def group_tasks(tasks: list[dict]):
    client = get_openai_client()

    prompt = f"""
You help organize tasks in a task management app.

Group the following tasks into clear, meaningful real-life categories.

Guidelines:
- Group tasks by topic or area of life (e.g. Work, Personal, Finance, Health, Household, Development)
- Use short, specific group names
- Avoid vague categories unless necessary
- Only use a fallback group named "Other" if a task truly does not fit any meaningful category
- Every task must be assigned to exactly one group
- Do not invent new tasks
- Keep tasks unchanged
- Do not wrap the JSON in markdown or code blocks.

Return ONLY valid JSON in this format:
{{
  "groups": [
    {{
      "group_name": "...",
      "tasks": [
        {{"id": 1, "title": "..."}}
      ]
    }}
  ]
}}

Tasks:
{json.dumps(tasks, ensure_ascii=False)}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content.strip()

    try:
        data = json.loads(content)
        return {"groups": data.get("groups", [])}
    except Exception as e:
        print("GROUP PARSE ERROR:", e)
        print("RAW:", content)
        return {"groups": []}
    

def sort_tasks_for_plan(tasks: list[dict]) -> list[dict]:
    today = datetime.now(timezone.utc).date()

    def sort_key(task: dict):
        priority = task.get("priority") or 3
        due_date = task.get("due_date")

        # Tasks without due date should still appear,
        # but usually after tasks with deadlines.
        if not due_date:
            return (
                1,          # tasks without due date come later
                999999,     # very large days_until_due
                priority,
            )

        try:
            due_dt = datetime.fromisoformat(
                due_date.replace("Z", "+00:00")
            )

            days_until_due = (
                due_dt.date() - today
            ).days

        except Exception:
            # fallback if parsing fails
            days_until_due = 999999

        return (
            0,                  # tasks with due date first
            days_until_due,     # earlier deadlines first
            priority,           # high priority first (1 before 2 before 3)
        )

    open_tasks = [
        task
        for task in tasks
        if not task.get("completed", False)
    ]

    return sorted(open_tasks, key=sort_key)

def create_task_plan(tasks: list[dict]):
    client = get_openai_client()

    sorted_tasks = sort_tasks_for_plan(tasks)

    prompt = f"""
You are an AI assistant that creates practical and realistic task execution plans for a task management app.

Your job:
- include every open task exactly once
- do not remove tasks
- do not add tasks
- keep the title unchanged
- tasks with due dates should primarily be ordered by the earliest deadlines first
- overdue tasks should appear before future tasks
- only flexibly reorder tasks that do not have a due_date
- for tasks without a due_date, place higher-priority and faster-to-complete tasks earlier in the plan
- maintain a practical and realistic execution order
- write a short practical reason for why each task appears in its position in the plan, considering deadlines, priority, dependencies, blocking importance, or estimated effort
- do not include any text outside JSON
- do not wrap the JSON in markdown or code blocks

Return ONLY valid JSON in this format:
{{
  "steps": [
    {{
      "id": 1,
      "title": "...",
      "reason": "..."
    }}
  ]
}}

Tasks in final order:
{json.dumps(sorted_tasks, ensure_ascii=False)}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content.strip()

    try:
        data = json.loads(content)
        steps = data.get("steps", [])

        task_by_id = {task["id"]: task for task in sorted_tasks}

        enriched_steps = []
        returned_ids = set()

        for step in steps:
            task_id = step.get("id")
            original_task = task_by_id.get(task_id)

            if original_task is None:
                continue

            returned_ids.add(task_id)

            enriched_steps.append(
                {
                    "id": original_task["id"],
                    "title": original_task["title"],
                    "reason": step.get("reason", ""),
                    "due_date": original_task.get("due_date"),
                    "priority": original_task.get("priority"),
                }
            )

        for task in sorted_tasks:
            if task["id"] not in returned_ids:
                enriched_steps.append(
                    {
                        "id": task["id"],
                        "title": task["title"],
                        "reason": "Included because every open task must appear in the plan.",
                        "due_date": task.get("due_date"),
                        "priority": task.get("priority"),
                    }
                )

        return {"steps": enriched_steps}

    except Exception as e:
        print("PARSE ERROR:", e)
        print("RAW:", content)
        return {"steps": []}