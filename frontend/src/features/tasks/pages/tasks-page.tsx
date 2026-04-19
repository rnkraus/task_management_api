import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createTask, getTasks } from "../api";
import { updateTaskCompleted } from "../api";

export default function TasksPage() {
  const queryClient = useQueryClient();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const tasksQuery = useQuery({
    queryKey: ["tasks"],
    queryFn: getTasks,
  });

  const createTaskMutation = useMutation({
    mutationFn: createTask,
    onSuccess: async (createdTask) => {
      console.log("Task created successfully:", createdTask);

      setTitle("");
      setDescription("");
      setErrorMessage("");
      await queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
    onError: (error) => {
      console.error("Create task error:", error);
      setErrorMessage("Failed to create task");
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

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErrorMessage("");

    createTaskMutation.mutate({
      title,
      description,
    });
  }

  if (tasksQuery.isLoading) {
    return <div>Loading tasks...</div>;
  }

  if (tasksQuery.isError) {
    return <div>Failed to load tasks.</div>;
  }

  return (
    <div>
      <h1>My Tasks</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <input
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>

        <div>
          <textarea
            placeholder="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        <button type="submit" disabled={createTaskMutation.isPending}>
          {createTaskMutation.isPending ? "Saving..." : "Create Task"}
        </button>
      </form>

      {errorMessage && <p>{errorMessage}</p>}

      {tasksQuery.data && tasksQuery.data.length === 0 && (
        <p>No tasks available.</p>
      )}

      <ul>
        {tasksQuery.data?.map((task) => (
          <li key={task.id}>
            <label>
              <input
                type="checkbox"
                checked={task.completed}
                onChange={() =>
                  toggleTaskMutation.mutate({
                    id: task.id,
                    completed: !task.completed,
                  })
                }
              />

              <strong
                style={{
                  textDecoration: task.completed ? "line-through" : "none",
                }}
              >
                {task.title}
              </strong>
            </label>

            {task.description && <span> - {task.description}</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}