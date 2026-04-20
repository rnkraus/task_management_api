import { api } from "../../lib/api-client";
import type { ImproveTaskRequest, ImproveTaskResponse } from "./types";

export async function improveTask(
  payload: ImproveTaskRequest
): Promise<ImproveTaskResponse> {
  const res = await api.post("/ai/improve-task", {
    title: payload.title,
    description: payload.description ?? null,
  });

  return res.data;
}