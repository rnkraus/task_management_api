import { api } from "../../lib/api-client";
import type { CreateTaskInput, Task } from "./types";

export async function getTasks(): Promise<Task[]> {
  const res = await api.get("/tasks", {
    params: {
      limit: 100,
      sort_by: "created_at",
      order: "desc",
    },
  });

  return res.data;
}

export async function createTask(payload: CreateTaskInput): Promise<Task> {
  const res = await api.post("/tasks", {
    title: payload.title,
    description: payload.description ?? null,
    completed: payload.completed ?? false,
  });

  return res.data;
}

export async function updateTaskCompleted(
  taskId: number,
  completed: boolean
) {
  const res = await api.patch(`/tasks/${taskId}`, {
    completed,
  });

  return res.data;
}