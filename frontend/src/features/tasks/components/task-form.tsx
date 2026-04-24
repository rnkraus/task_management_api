type Props = {
  title: string;
  description: string;
  dueDate: string;
  priority: number;
  errorMessage: string;
  aiErrorMessage: string;
  aiSuggestedTitle: string;
  aiSuggestedDescription: string;
  isCreating: boolean;
  isImproving: boolean;
  onTitleChange: (value: string) => void;
  onDescriptionChange: (value: string) => void;
  onDueDateChange: (value: string) => void;
  onPriorityChange: (value: number) => void;
  onSubmit: (e: React.FormEvent) => void;
  onImproveTask: () => void;
  onApplyAiSuggestion: () => void;
};

export default function TaskForm({
  title,
  description,
  dueDate,
  priority,
  errorMessage,
  aiErrorMessage,
  aiSuggestedTitle,
  aiSuggestedDescription,
  isCreating,
  isImproving,
  onTitleChange,
  onDescriptionChange,
  onDueDateChange,
  onPriorityChange,
  onSubmit,
  onImproveTask,
  onApplyAiSuggestion,
}: Props) {
  return (
    <section className="section">
      <h2 className="section-title">Create Task</h2>

      <form onSubmit={onSubmit} className="form-grid">
        <input
          className="input"
          placeholder="Title"
          value={title}
          onChange={(e) => onTitleChange(e.target.value)}
        />

        <textarea
          className="textarea"
          placeholder="Description"
          value={description}
          onChange={(e) => onDescriptionChange(e.target.value)}
        />

        <input
          className="input"
          type="datetime-local"
          value={dueDate}
          onChange={(e) => onDueDateChange(e.target.value)}
        />

        <select
          className="select"
          value={priority}
          onChange={(e) => onPriorityChange(Number(e.target.value))}
        >
          <option value={1}>Low</option>
          <option value={2}>Medium</option>
          <option value={3}>High</option>
        </select>

        <div className="button-row">
          <button className="button" type="submit" disabled={isCreating}>
            {isCreating ? "Saving..." : "Create Task"}
          </button>

          <button
            className="button button-secondary"
            type="button"
            onClick={onImproveTask}
            disabled={isImproving}
          >
            {isImproving ? "Improving..." : "Improve with AI"}
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

          <button
            className="button"
            type="button"
            onClick={onApplyAiSuggestion}
          >
            Apply Suggestion
          </button>
        </div>
      )}
    </section>
  );
}