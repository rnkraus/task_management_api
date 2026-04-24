type AiPlanStep = {
  id: number;
  title: string;
  reason: string;
  due_date?: string | null;
};

type AiGroup = {
  group_name: string;
  tasks: {
    id: number;
    title: string;
  }[];
};

type Props = {
  aiPlan: AiPlanStep[];
  aiGroups: AiGroup[];
  aiPlanErrorMessage: string;
  aiGroupsErrorMessage: string;
  isGeneratingPlan: boolean;
  isGroupingTasks: boolean;
  onGeneratePlan: () => void;
  onGroupTasks: () => void;
};

export default function AiToolsPanel({
  aiPlan,
  aiGroups,
  aiPlanErrorMessage,
  aiGroupsErrorMessage,
  isGeneratingPlan,
  isGroupingTasks,
  onGeneratePlan,
  onGroupTasks,
}: Props) {
  return (
    <section className="section">
      <h2 className="section-title">AI Tools</h2>

      <div className="button-row">
        <button
          className="button"
          type="button"
          onClick={onGeneratePlan}
          disabled={isGeneratingPlan}
        >
          {isGeneratingPlan ? "Generating plan..." : "Generate AI Plan"}
        </button>

        <button
          className="button button-secondary"
          type="button"
          onClick={onGroupTasks}
          disabled={isGroupingTasks}
        >
          {isGroupingTasks ? "Grouping tasks..." : "Group Tasks with AI"}
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

                {step.due_date && (
                  <div className="muted-text">
                    Due: {new Date(step.due_date).toLocaleString()}
                  </div>
                )}
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
  );
}