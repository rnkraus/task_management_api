import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createTask, deleteTask, getTasks, updateTaskCompleted } from "../api";

export default function TasksPage() {
  const queryClient = useQueryClient();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [search, setSearch] = useState("");
  const [completedFilter, setCompletedFilter] = useState<
    "all" | "completed" | "open"
  >("all");

  const tasksQuery = useQuery({
    queryKey: ["tasks", search, completedFilter],
    queryFn: () =>
      getTasks({
        search,
        completed:
          completedFilter === "all"
            ? undefined
            : completedFilter === "completed",
      }),
  });

  const createTaskMutation = useMutation({
    mutationFn: createTask,
    onSuccess: async () => {
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

  const deleteTaskMutation = useMutation({
    mutationFn: (taskId: number) => deleteTask(taskId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
    onError: (error) => {
      console.error("Delete task error:", error);
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErrorMessage("");

    if (!title.trim()) {
      setErrorMessage("Title is required");
      return;
    }

    createTaskMutation.mutate({
      title: title.trim(),
      description: description.trim(),
    });
  }

  function handleDelete(taskId: number) {
    const confirmed = confirm("Are you sure you want to delete this task?");
    if (!confirmed) return;

    deleteTaskMutation.mutate(taskId);
  }

  function handleLogout() {
    localStorage.removeItem("access_token");
    window.location.href = "/login";
  }

  if (tasksQuery.isLoading) {
    return <div>Loading tasks...</div>;
  }

  if (tasksQuery.isError) {
    return <div>Failed to load tasks.</div>;
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1>My Tasks</h1>
        <button onClick={handleLogout}>Logout</button>
      </div>

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

      {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}

      <div style={{ marginTop: "16px", marginBottom: "16px" }}>
        <input
          placeholder="Search tasks"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ marginRight: "10px" }}
        />

        <select
          value={completedFilter}
          onChange={(e) =>
            setCompletedFilter(
              e.target.value as "all" | "completed" | "open"
            )
          }
        >
          <option value="all">All</option>
          <option value="open">Open</option>
          <option value="completed">Completed</option>
        </select>
      </div>

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

            <button
              type="button"
              onClick={() => handleDelete(task.id)}
              style={{ marginLeft: "10px" }}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}