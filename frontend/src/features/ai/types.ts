export type ImproveTaskRequest = {
  title: string;
  description?: string;
};

export type ImproveTaskResponse = {
  suggested_title: string;
  suggested_description: string | null;
};

export type PlannedTaskStep = {
  id: number;
  title: string;
  reason: string;
};

export type TaskPlanResponse = {
  steps: PlannedTaskStep[];
};