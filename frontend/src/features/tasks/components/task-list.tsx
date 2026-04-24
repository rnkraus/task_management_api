import type { Task } from "../types";

type Props = {
  tasks: Task[] | undefined;
  editingTaskId: number | null;
  editTitle: string;
  editDescription: string;
  editDueDate: string;
  editPriority: number;
  isUpdating: boolean;
  onToggleCompleted: (id: number, completed: boolean) => void;
  onStartEditing: (task: Task) => void;
  onCancelEditing: () => void;
  onSaveEdit: (taskId: number) => void;
  onDelete: (taskId: number) => void;
  onEditTitleChange: (value: string) => void;
  onEditDescriptionChange: (value: string) => void;
  onEditDueDateChange: (value: string) => void;
  onEditPriorityChange: (value: number) => void;
};

export default function TaskList({
  tasks,
  editingTaskId,
  editTitle,
  editDescription,
  editDueDate,
  editPriority,
  isUpdating,
  onToggleCompleted,
  onStartEditing,
  onCancelEditing,
  onSaveEdit,
  onDelete,
  onEditTitleChange,
  onEditDescriptionChange,
  onEditDueDateChange,
  onEditPriorityChange,
}: Props) {
  function formatPriority(priority: number) {
    if (priority === 1) return "Low";
    if (priority === 2) return "Medium";
    return "High";
  }

  if (tasks && tasks.length === 0) {
    return (
      <section className="section">
        <h2 className="section-title">Task List</h2>

        <div className="empty-state">
          <p>No tasks available.</p>
          <p className="muted-text">Create your first task to get started.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="section">
      <h2 className="section-title">Task List</h2>

      <ul className="task-list">
        {tasks?.map((task) => (
          <li key={task.id} className="task-item">
            {editingTaskId === task.id ? (
              <div className="form-grid">
                <input
                  className="input"
                  value={editTitle}
                  onChange={(e) => onEditTitleChange(e.target.value)}
                  placeholder="Edit title"
                />

                <textarea
                  className="textarea"
                  value={editDescription}
                  onChange={(e) => onEditDescriptionChange(e.target.value)}
                  placeholder="Edit description"
                />

                <input
                  className="input"
                  type="datetime-local"
                  value={editDueDate}
                  onChange={(e) => onEditDueDateChange(e.target.value)}
                />

                <select
                  className="select"
                  value={editPriority}
                  onChange={(e) => onEditPriorityChange(Number(e.target.value))}
                >
                  <option value={1}>Low</option>
                  <option value={2}>Medium</option>
                  <option value={3}>High</option>
                </select>

                <div className="button-row">
                  <button
                    className="button"
                    type="button"
                    onClick={() => onSaveEdit(task.id)}
                    disabled={isUpdating}
                  >
                    {isUpdating ? "Saving..." : "Save"}
                  </button>

                  <button
                    className="button button-secondary"
                    type="button"
                    onClick={onCancelEditing}
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
                      onToggleCompleted(task.id, !task.completed)
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
                    onClick={() => onStartEditing(task)}
                  >
                    Edit
                  </button>

                  <button
                    className="button button-danger"
                    type="button"
                    onClick={() => onDelete(task.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}