import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createTask,
  deleteTask,
  getTasks,
  updateTask,
  updateTaskCompleted,
} from "../api";
import { getTaskPlan, improveTask } from "../../ai/api";

export default function TasksPage() {
  const queryClient = useQueryClient();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [search, setSearch] = useState("");
  const [completedFilter, setCompletedFilter] = useState<
    "all" | "completed" | "open"
  >("all");

  const [editingTaskId, setEditingTaskId] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");

  const [aiSuggestedTitle, setAiSuggestedTitle] = useState("");
  const [aiSuggestedDescription, setAiSuggestedDescription] = useState("");
  const [aiErrorMessage, setAiErrorMessage] = useState("");

  const [aiPlan, setAiPlan] = useState<
    { id: number; title: string; reason: string }[]
  >([]);
  const [aiPlanErrorMessage, setAiPlanErrorMessage] = useState("");

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
      setAiSuggestedTitle("");
      setAiSuggestedDescription("");
      setAiErrorMessage("");
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

  const updateTaskMutation = useMutation({
    mutationFn: ({
      id,
      title,
      description,
    }: {
      id: number;
      title: string;
      description: string;
    }) =>
      updateTask(id, {
        title,
        description,
      }),
    onSuccess: async () => {
      setEditingTaskId(null);
      setEditTitle("");
      setEditDescription("");
      await queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
    onError: (error) => {
      console.error("Update task error:", error);
      setErrorMessage("Failed to update task");
    },
  });

  const improveTaskMutation = useMutation({
    mutationFn: improveTask,
    onSuccess: (data) => {
      setAiSuggestedTitle(data.suggested_title);
      setAiSuggestedDescription(data.suggested_description ?? "");
      setAiErrorMessage("");
    },
    onError: (error) => {
      console.error("Improve task error:", error);
      setAiErrorMessage("Failed to improve task");
    },
  });

  const taskPlanMutation = useMutation({
    mutationFn: getTaskPlan,
    onSuccess: (data) => {
      setAiPlan(data.steps);
      setAiPlanErrorMessage("");
    },
    onError: (error) => {
      console.error("Get task plan error:", error);
      setAiPlanErrorMessage("Failed to generate AI plan");
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

  function handleImproveTask() {
    setAiErrorMessage("");

    if (!title.trim()) {
      setAiErrorMessage("Title is required before using AI");
      return;
    }

    improveTaskMutation.mutate({
      title: title.trim(),
      description: description.trim(),
    });
  }

  function applyAiSuggestion() {
    setTitle(aiSuggestedTitle);
    setDescription(aiSuggestedDescription);
  }

  function handleGenerateAiPlan() {
    setAiPlanErrorMessage("");
    taskPlanMutation.mutate();
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

  function startEditing(task: {
    id: number;
    title: string;
    description: string | null;
  }) {
    setEditingTaskId(task.id);
    setEditTitle(task.title);
    setEditDescription(task.description ?? "");
    setErrorMessage("");
  }

  function cancelEditing() {
    setEditingTaskId(null);
    setEditTitle("");
    setEditDescription("");
  }

  function saveEdit(taskId: number) {
    setErrorMessage("");

    if (!editTitle.trim()) {
      setErrorMessage("Title is required");
      return;
    }

    updateTaskMutation.mutate({
      id: taskId,
      title: editTitle.trim(),
      description: editDescription.trim(),
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

      <div style={{ marginTop: "10px" }}>
        <button
          type="button"
          onClick={handleImproveTask}
          disabled={improveTaskMutation.isPending}
        >
          {improveTaskMutation.isPending ? "Improving..." : "Improve with AI"}
        </button>
      </div>

      {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}
      {aiErrorMessage && <p style={{ color: "red" }}>{aiErrorMessage}</p>}

      {(aiSuggestedTitle || aiSuggestedDescription) && (
        <div style={{ marginTop: "16px", marginBottom: "16px" }}>
          <h2>AI Suggestion</h2>
          <p>
            <strong>Suggested title:</strong> {aiSuggestedTitle}
          </p>
          <p>
            <strong>Suggested description:</strong>{" "}
            {aiSuggestedDescription || "None"}
          </p>

          <button type="button" onClick={applyAiSuggestion}>
            Apply Suggestion
          </button>
        </div>
      )}

      <div style={{ marginTop: "16px", marginBottom: "16px" }}>
        <button
          type="button"
          onClick={handleGenerateAiPlan}
          disabled={taskPlanMutation.isPending}
        >
          {taskPlanMutation.isPending
            ? "Generating plan..."
            : "Generate AI Plan"}
        </button>
      </div>

      {aiPlanErrorMessage && (
        <p style={{ color: "red" }}>{aiPlanErrorMessage}</p>
      )}

      {aiPlan.length > 0 && (
        <div style={{ marginTop: "16px", marginBottom: "16px" }}>
          <h2>AI Task Plan</h2>
          <ol>
            {aiPlan.map((step) => (
              <li key={step.id}>
                <strong>{step.title}</strong> - {step.reason}
              </li>
            ))}
          </ol>
        </div>
      )}

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
          <li key={task.id} style={{ marginBottom: "12px" }}>
            {editingTaskId === task.id ? (
              <div>
                <div>
                  <input
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    placeholder="Edit title"
                  />
                </div>

                <div>
                  <textarea
                    value={editDescription}
                    onChange={(e) => setEditDescription(e.target.value)}
                    placeholder="Edit description"
                  />
                </div>

                <button
                  type="button"
                  onClick={() => saveEdit(task.id)}
                  disabled={updateTaskMutation.isPending}
                >
                  {updateTaskMutation.isPending ? "Saving..." : "Save"}
                </button>

                <button
                  type="button"
                  onClick={cancelEditing}
                  style={{ marginLeft: "8px" }}
                >
                  Cancel
                </button>
              </div>
            ) : (
              <div>
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
                  onClick={() => startEditing(task)}
                  style={{ marginLeft: "10px" }}
                >
                  Edit
                </button>

                <button
                  type="button"
                  onClick={() => handleDelete(task.id)}
                  style={{ marginLeft: "10px" }}
                >
                  Delete
                </button>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}