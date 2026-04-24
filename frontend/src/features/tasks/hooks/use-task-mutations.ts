import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createTask,
  deleteTask,
  updateTask,
  updateTaskCompleted,
} from "../api";

export function useTaskMutations() {
  const queryClient = useQueryClient();

  const createTaskMutation = useMutation({
    mutationFn: createTask,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
    onError: (error) => {
      console.error("Create task error:", error);
    },
  });

  const toggleTaskMutation = useMutation({
    mutationFn: ({ id, completed }: { id: number; completed: boolean }) =>
      updateTaskCompleted(id, completed),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
    onError: (error) => {
      console.error("Toggle task error:", error);
    },
  });

  const updateTaskMutation = useMutation({
    mutationFn: ({
      id,
      title,
      description,
      due_date,
      priority,
    }: {
      id: number;
      title: string;
      description: string;
      due_date: string | null;
      priority: number;
    }) =>
      updateTask(id, {
        title,
        description,
        due_date,
        priority,
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
    onError: (error) => {
      console.error("Update task error:", error);
    },
  });

  const deleteTaskMutation = useMutation({
    mutationFn: (taskId: number) => deleteTask(taskId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
    onError: (error) => {
      console.error("Delete task error:", error);
    },
  });

  return {
    createTaskMutation,
    toggleTaskMutation,
    updateTaskMutation,
    deleteTaskMutation,
  };
}