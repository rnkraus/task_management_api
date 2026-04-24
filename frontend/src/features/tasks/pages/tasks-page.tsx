import { useState } from "react";

import { useCurrentUser } from "../../auth/hooks/use-current-user";
import { useAiTools } from "../../ai/hooks/use-ai-tools";
import AiToolsPanel from "../../ai/components/ai-tools-panel";

import TaskForm from "../components/task-form";
import TaskFilters from "../components/task-filters";
import TaskList from "../components/task-list";
import { useTaskMutations } from "../hooks/use-task-mutations";
import { useTaskQuery } from "../hooks/use-tasks";

export default function TasksPage() {
  const currentUserQuery = useCurrentUser();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const [search, setSearch] = useState("");
  const [completedFilter, setCompletedFilter] = useState<
    "all" | "completed" | "open"
  >("all");

  const [sortBy, setSortBy] = useState<
    "title" | "created_at" | "priority" | "due_date"
  >("due_date");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

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
    {
      id: number;
      title: string;
      reason: string;
      due_date?: string | null;
    }[]
  >([]);
  const [aiPlanErrorMessage, setAiPlanErrorMessage] = useState("");

  const [aiGroups, setAiGroups] = useState<
    { group_name: string; tasks: { id: number; title: string }[] }[]
  >([]);
  const [aiGroupsErrorMessage, setAiGroupsErrorMessage] = useState("");

  const tasksQuery = useTaskQuery({
    search,
    completedFilter,
    sortBy,
    sortOrder,
  });

  const {
    createTaskMutation,
    toggleTaskMutation,
    updateTaskMutation,
    deleteTaskMutation,
  } = useTaskMutations();

  const { improveTaskMutation, taskPlanMutation, groupedTasksMutation } =
    useAiTools();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErrorMessage("");

    if (!title.trim()) {
      setErrorMessage("Title is required");
      return;
    }

    createTaskMutation.mutate(
      {
        title: title.trim(),
        description: description.trim(),
        due_date: dueDate || null,
        priority,
      },
      {
        onSuccess: () => {
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
        },
        onError: () => {
          setErrorMessage("Failed to create task");
        },
      }
    );
  }

  function handleImproveTask() {
    setAiErrorMessage("");

    if (!title.trim()) {
      setAiErrorMessage("Title is required before using AI");
      return;
    }

    improveTaskMutation.mutate(
      {
        title: title.trim(),
        description: description.trim(),
      },
      {
        onSuccess: (data) => {
          setAiSuggestedTitle(data.suggested_title);
          setAiSuggestedDescription(data.suggested_description ?? "");
          setAiErrorMessage("");
        },
        onError: () => {
          setAiErrorMessage("Failed to improve task");
        },
      }
    );
  }

  function applyAiSuggestion() {
    setTitle(aiSuggestedTitle);
    setDescription(aiSuggestedDescription);
  }

  function handleGenerateAiPlan() {
    setAiPlanErrorMessage("");

    taskPlanMutation.mutate(undefined, {
      onSuccess: (data) => {
        setAiPlan(data.steps);
        setAiPlanErrorMessage("");
      },
      onError: () => {
        setAiPlanErrorMessage("Failed to generate AI plan");
      },
    });
  }

  function handleGroupTasksWithAi() {
    setAiGroupsErrorMessage("");

    groupedTasksMutation.mutate(undefined, {
      onSuccess: (data) => {
        setAiGroups(data.groups);
        setAiGroupsErrorMessage("");
      },
      onError: () => {
        setAiGroupsErrorMessage("Failed to group tasks");
      },
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

  function formatDateTimeForInput(dateString: string | null) {
    if (!dateString) return "";
    return new Date(dateString).toISOString().slice(0, 16);
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

    updateTaskMutation.mutate(
      {
        id: taskId,
        title: editTitle.trim(),
        description: editDescription.trim(),
        due_date: editDueDate || null,
        priority: editPriority,
      },
      {
        onSuccess: () => {
          setEditingTaskId(null);
          setEditTitle("");
          setEditDescription("");
          setEditDueDate("");
          setEditPriority(3);
        },
        onError: () => {
          setErrorMessage("Failed to update task");
        },
      }
    );
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

      <TaskForm
        title={title}
        description={description}
        dueDate={dueDate}
        priority={priority}
        errorMessage={errorMessage}
        aiErrorMessage={aiErrorMessage}
        aiSuggestedTitle={aiSuggestedTitle}
        aiSuggestedDescription={aiSuggestedDescription}
        isCreating={createTaskMutation.isPending}
        isImproving={improveTaskMutation.isPending}
        onTitleChange={setTitle}
        onDescriptionChange={setDescription}
        onDueDateChange={setDueDate}
        onPriorityChange={setPriority}
        onSubmit={handleSubmit}
        onImproveTask={handleImproveTask}
        onApplyAiSuggestion={applyAiSuggestion}
      />

      <AiToolsPanel
        aiPlan={aiPlan}
        aiGroups={aiGroups}
        aiPlanErrorMessage={aiPlanErrorMessage}
        aiGroupsErrorMessage={aiGroupsErrorMessage}
        isGeneratingPlan={taskPlanMutation.isPending}
        isGroupingTasks={groupedTasksMutation.isPending}
        onGeneratePlan={handleGenerateAiPlan}
        onGroupTasks={handleGroupTasksWithAi}
      />

      <TaskFilters
        search={search}
        completedFilter={completedFilter}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSearchChange={setSearch}
        onCompletedFilterChange={setCompletedFilter}
        onSortByChange={setSortBy}
        onSortOrderChange={setSortOrder}
      />

      <TaskList
        tasks={tasksQuery.data}
        editingTaskId={editingTaskId}
        editTitle={editTitle}
        editDescription={editDescription}
        editDueDate={editDueDate}
        editPriority={editPriority}
        isUpdating={updateTaskMutation.isPending}
        onToggleCompleted={(id, completed) =>
          toggleTaskMutation.mutate({ id, completed })
        }
        onStartEditing={startEditing}
        onCancelEditing={cancelEditing}
        onSaveEdit={saveEdit}
        onDelete={handleDelete}
        onEditTitleChange={setEditTitle}
        onEditDescriptionChange={setEditDescription}
        onEditDueDateChange={setEditDueDate}
        onEditPriorityChange={setEditPriority}
      />
    </div>
  );
}