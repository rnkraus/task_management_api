import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createTask,
  deleteTask,
  getTasks,
  updateTask,
  updateTaskCompleted,
} from "../api";
import { getGroupedTasks, getTaskPlan, improveTask } from "../../ai/api";
import { useCurrentUser } from "../../auth/hooks/use-current-user";

export default function TasksPage() {
  const currentUserQuery = useCurrentUser();
  const queryClient = useQueryClient();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [search, setSearch] = useState("");
  const [completedFilter, setCompletedFilter] = useState<
    "all" | "completed" | "open"
  >("all");
  const [dueDate, setDueDate] = useState("");
  const [priority, setPriority] = useState(3);

  const [editingTaskId, setEditingTaskId] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editDueDate, setEditDueDate] = useState("");
  const [editPriority, setEditPriority] = useState(3);

  const [aiSuggestedTitle, setAiSuggestedTitle] = useState("");
  const [aiSuggestedDescription, setAiSuggestedDescription] = useState("");
  const [aiErrorMessage, setAiErrorMessage] = useState("");

  const [aiPlan, setAiPlan] = useState<
    { id: number; title: string; reason: string }[]
  >([]);
  const [aiPlanErrorMessage, setAiPlanErrorMessage] = useState("");

  const [aiGroups, setAiGroups] = useState<
    { group_name: string; tasks: { id: number; title: string }[] }[]
  >([]);
  const [aiGroupsErrorMessage, setAiGroupsErrorMessage] = useState("");

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
      setDueDate("");
      setPriority(3);
      setErrorMessage("");

      setAiSuggestedTitle("");
      setAiSuggestedDescription("");
      setAiErrorMessage("");
      setAiPlan([]);
      setAiGroups([]);

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
      setEditingTaskId(null);
      setEditTitle("");
      setEditDescription("");
      setEditDueDate("");
      setEditPriority(3);
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

  const groupedTasksMutation = useMutation({
    mutationFn: getGroupedTasks,
    onSuccess: (data) => {
      setAiGroups(data.groups);
      setAiGroupsErrorMessage("");
    },
    onError: (error) => {
      console.error("Get grouped tasks error:", error);
      setAiGroupsErrorMessage("Failed to group tasks");
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
      due_date: dueDate || null,
      priority,
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

  function handleGroupTasksWithAi() {
    setAiGroupsErrorMessage("");
    groupedTasksMutation.mutate();
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

  function formatDateTimeForInput(dateString: string | null) {
    if (!dateString) return "";
    return new Date(dateString).toISOString().slice(0, 16);
  }

  function formatPriority(priorityValue: number) {
    if (priorityValue === 1) return "High";
    if (priorityValue === 2) return "Medium";
    return "Low";
  }

  function startEditing(task: {
    id: number;
    title: string;
    description: string | null;
    due_date: string | null;
    priority: number;
  }) {
    setEditingTaskId(task.id);
    setEditTitle(task.title);
    setEditDescription(task.description ?? "");
    setEditDueDate(formatDateTimeForInput(task.due_date));
    setEditPriority(task.priority ?? 3);
    setErrorMessage("");
  }

  function cancelEditing() {
    setEditingTaskId(null);
    setEditTitle("");
    setEditDescription("");
    setEditDueDate("");
    setEditPriority(3);
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
      due_date: editDueDate || null,
      priority: editPriority,
    });
  }

  if (tasksQuery.isLoading) {
    return (
      <div className="page">
        <div className="empty-state">Loading tasks...</div>
      </div>
    );
  }

  if (tasksQuery.isError) {
    return (
      <div className="page">
        <div className="empty-state">Failed to load tasks.</div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">My Tasks</h1>

        <div className="button-row">
          {currentUserQuery.data && (
            <span className="muted-text">
              {currentUserQuery.data.name} ({currentUserQuery.data.email})
            </span>
          )}

          <button className="button button-secondary" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>

      <section className="section">
        <h2 className="section-title">Create Task</h2>

        <form onSubmit={handleSubmit} className="form-grid">
          <input
            className="input"
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />

          <textarea
            className="textarea"
            placeholder="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />

          <input
            className="input"
            type="datetime-local"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
          />

          <select
            className="select"
            value={priority}
            onChange={(e) => setPriority(Number(e.target.value))}
          >
            <option value={1}>High</option>
            <option value={2}>Medium</option>
            <option value={3}>Low</option>
          </select>

          <div className="button-row">
            <button
              className="button"
              type="submit"
              disabled={createTaskMutation.isPending}
            >
              {createTaskMutation.isPending ? "Saving..." : "Create Task"}
            </button>

            <button
              className="button button-secondary"
              type="button"
              onClick={handleImproveTask}
              disabled={improveTaskMutation.isPending}
            >
              {improveTaskMutation.isPending
                ? "Improving..."
                : "Improve with AI"}
            </button>
          </div>
        </form>

        {errorMessage && <p className="error-text">{errorMessage}</p>}
        {aiErrorMessage && <p className="error-text">{aiErrorMessage}</p>}

        {(aiSuggestedTitle || aiSuggestedDescription) && (
          <div className="ai-box" style={{ marginTop: "16px" }}>
            <h3>AI Suggestion</h3>
            <p>
              <strong>Suggested title:</strong> {aiSuggestedTitle}
            </p>
            <p>
              <strong>Suggested description:</strong>{" "}
              {aiSuggestedDescription || "None"}
            </p>

            <button className="button" type="button" onClick={applyAiSuggestion}>
              Apply Suggestion
            </button>
          </div>
        )}
      </section>

      <section className="section">
        <h2 className="section-title">AI Tools</h2>

        <div className="button-row">
          <button
            className="button"
            type="button"
            onClick={handleGenerateAiPlan}
            disabled={taskPlanMutation.isPending}
          >
            {taskPlanMutation.isPending
              ? "Generating plan..."
              : "Generate AI Plan"}
          </button>

          <button
            className="button button-secondary"
            type="button"
            onClick={handleGroupTasksWithAi}
            disabled={groupedTasksMutation.isPending}
          >
            {groupedTasksMutation.isPending
              ? "Grouping tasks..."
              : "Group Tasks with AI"}
          </button>
        </div>

        {aiPlanErrorMessage && <p className="error-text">{aiPlanErrorMessage}</p>}
        {aiGroupsErrorMessage && (
          <p className="error-text">{aiGroupsErrorMessage}</p>
        )}

        {aiPlan.length > 0 && (
          <div className="ai-box" style={{ marginTop: "16px" }}>
            <h3>AI Task Plan</h3>
            <ol>
              {aiPlan.map((step) => (
                <li key={step.id}>
                  <strong>{step.title}</strong> - {step.reason}
                </li>
              ))}
            </ol>
          </div>
        )}

        {aiGroups.length > 0 && (
          <div className="ai-box" style={{ marginTop: "16px" }}>
            <h3>AI Task Groups</h3>

            {aiGroups.map((group) => (
              <div key={group.group_name} style={{ marginBottom: "12px" }}>
                <h4>{group.group_name}</h4>
                <ul>
                  {group.tasks.map((task) => (
                    <li key={task.id}>{task.title}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="section">
        <h2 className="section-title">Task Controls</h2>

        <div className="controls-row">
          <input
            className="input"
            placeholder="Search tasks"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />

          <select
            className="select"
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
      </section>

      <section className="section">
        <h2 className="section-title">Task List</h2>

        {tasksQuery.data && tasksQuery.data.length === 0 ? (
          <div className="empty-state">
            <p>No tasks available.</p>
            <p className="muted-text">Create your first task to get started.</p>
          </div>
        ) : (
          <ul className="task-list">
            {tasksQuery.data?.map((task) => (
              <li key={task.id} className="task-item">
                {editingTaskId === task.id ? (
                  <div className="form-grid">
                    <input
                      className="input"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      placeholder="Edit title"
                    />

                    <textarea
                      className="textarea"
                      value={editDescription}
                      onChange={(e) => setEditDescription(e.target.value)}
                      placeholder="Edit description"
                    />

                    <input
                      className="input"
                      type="datetime-local"
                      value={editDueDate}
                      onChange={(e) => setEditDueDate(e.target.value)}
                    />

                    <select
                      className="select"
                      value={editPriority}
                      onChange={(e) => setEditPriority(Number(e.target.value))}
                    >
                      <option value={1}>High</option>
                      <option value={2}>Medium</option>
                      <option value={3}>Low</option>
                    </select>

                    <div className="button-row">
                      <button
                        className="button"
                        type="button"
                        onClick={() => saveEdit(task.id)}
                        disabled={updateTaskMutation.isPending}
                      >
                        {updateTaskMutation.isPending ? "Saving..." : "Save"}
                      </button>

                      <button
                        className="button button-secondary"
                        type="button"
                        onClick={cancelEditing}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="task-main">
                    <div className="task-info">
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

                      <div>
                        <div
                          className={
                            task.completed
                              ? "task-title task-title-completed"
                              : "task-title"
                          }
                        >
                          {task.title}
                        </div>

                        {task.description && (
                          <div className="task-description">
                            {task.description}
                          </div>
                        )}

                        {task.due_date && (
                          <div className="muted-text">
                            Due: {new Date(task.due_date).toLocaleString()}
                          </div>
                        )}

                        <div className="muted-text">
                          Priority: {formatPriority(task.priority)}
                        </div>
                      </div>
                    </div>

                    <div className="button-row">
                      <button
                        className="button button-secondary"
                        type="button"
                        onClick={() => startEditing(task)}
                      >
                        Edit
                      </button>

                      <button
                        className="button button-danger"
                        type="button"
                        onClick={() => handleDelete(task.id)}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}