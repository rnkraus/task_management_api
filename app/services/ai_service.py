from openai import OpenAI
from app.core.config import settings
import json

client = OpenAI(api_key=settings.openai_api_key)


def improve_task(title: str, description: str | None):
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