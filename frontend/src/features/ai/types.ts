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

export type GroupedTaskItem = {
  id: number;
  title: string;
};

export type TaskGroup = {
  group_name: string;
  tasks: GroupedTaskItem[];
};

export type GroupTasksResponse = {
  groups: TaskGroup[];
};