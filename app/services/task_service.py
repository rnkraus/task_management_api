tasks = []
task_id_counter = 1


def create_task(task_data):
    global task_id_counter

    new_task = {
        "id": task_id_counter,
        "title": task_data.title,
        "completed": task_data.completed,
    }

    tasks.append(new_task)
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
            return task
    return None


def patch_task(task_id: int, task_data):
    for task in tasks:
        if task["id"] == task_id:
            if task_data.title is not None:
                task["title"] = task_data.title
            if task_data.completed is not None:
                task["completed"] = task_data.completed
            return task
    return None


def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            return tasks.pop(index)
    return None