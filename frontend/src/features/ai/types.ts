export type ImproveTaskRequest = {
  title: string;
  description?: string;
};

export type ImproveTaskResponse = {
  suggested_title: string;
  suggested_description: string | null;
};