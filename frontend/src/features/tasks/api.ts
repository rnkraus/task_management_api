import { api } from "../../lib/api-client";
import type { Task } from "./types";

export async function getTasks(): Promise<Task[]> {
  const res = await api.get("/tasks");
  return res.data;
}