import { useMutation } from "@tanstack/react-query";
import { getGroupedTasks, getTaskPlan, improveTask } from "../api";

export function useAiTools() {
  const improveTaskMutation = useMutation({
    mutationFn: improveTask,
    onError: (error) => {
      console.error("Improve task error:", error);
    },
  });

  const taskPlanMutation = useMutation({
    mutationFn: getTaskPlan,
    onError: (error) => {
      console.error("Get task plan error:", error);
    },
  });

  const groupedTasksMutation = useMutation({
    mutationFn: getGroupedTasks,
    onError: (error) => {
      console.error("Get grouped tasks error:", error);
    },
  });

  return {
    improveTaskMutation,
    taskPlanMutation,
    groupedTasksMutation,
  };
}