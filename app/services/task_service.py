import json
from app.core.config import DATA_FILE

def load_tasks():
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump([], file)
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def save_tasks():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=4)


def get_next_task_id():
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1

tasks = load_tasks()
task_id_counter = get_next_task_id()


def create_task(task_data):
    global task_id_counter

    new_task = {
        "id": task_id_counter,
        "title": task_data.title,
        "completed": task_data.completed,
    }

    tasks.append(new_task)
    save_tasks()
    task_id_counter += 1
    return new_task


def get_all_tasks():
    return tasks


def get_task_by_id(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def update_task(task_id: int, task_data):
    for task in tasks:
        if task["id"] == task_id:
            task["title"] = task_data.title
            task["completed"] = task_data.completed
            save_tasks()
            return task
    return None


def patch_task(task_id: int, task_data):
    for task in tasks:
        if task["id"] == task_id:
            if task_data.title is not None:
                task["title"] = task_data.title
            if task_data.completed is not None:
                task["completed"] = task_data.completed
            save_tasks()
            return task
    return None


def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            deleted_task = tasks.pop(index)
            save_tasks()
            return deleted_task
    return None