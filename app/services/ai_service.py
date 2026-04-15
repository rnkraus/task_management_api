from openai import OpenAI
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
    )

    content = response.choices[0].message.content.strip()

    try:
        data = json.loads(content)
        return {"groups": data.get("groups", [])}
    except Exception:
        return {"groups": []}