import { api } from "../../lib/api-client";
import type { CreateTaskInput, Task } from "./types";

type GetTasksParams = {
  search?: string;
  completed?: boolean;
};

export async function getTasks(params?: GetTasksParams): Promise<Task[]> {
  const res = await api.get("/tasks", {
    params: {
      limit: 100,
      sort_by: "created_at",
      order: "desc",
      search: params?.search || undefined,
      completed: params?.completed,
    },
  });

  return res.data;
}

export async function createTask(payload: CreateTaskInput): Promise<Task> {
  const res = await api.post("/tasks", {
    title: payload.title,
    description: payload.description ?? null,
    completed: payload.completed ?? false,
    due_date: payload.due_date ?? null,
    priority: payload.priority ?? 3,
  });

  return res.data;
}

export async function updateTaskCompleted(
  taskId: number,
  completed: boolean
): Promise<Task> {
  const res = await api.patch(`/tasks/${taskId}`, {
    completed,
  });

  return res.data;
}

export async function deleteTask(taskId: number): Promise<Task> {
  const res = await api.delete(`/tasks/${taskId}`);
  return res.data;
}

export async function updateTask(
  taskId: number,
  payload: {
    title?: string;
    description?: string;
    completed?: boolean;
    due_date?: string | null;
    priority?: number;
  }
): Promise<Task> {
  const res = await api.patch(`/tasks/${taskId}`, payload);
  return res.data;
}