export type Task = {
  id: number;
  title: string;
  completed: boolean;
  description: string | null;
  user_id: number;
  created_at: string;
  updated_at: string;
};

export type CreateTaskInput = {
  title: string;
  description?: string;
  completed?: boolean;
};