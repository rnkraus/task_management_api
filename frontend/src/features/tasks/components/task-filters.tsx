type SortBy = "title" | "created_at" | "priority" | "due_date";

type Props = {
  search: string;
  completedFilter: "all" | "completed" | "open";
  sortBy: SortBy;
  sortOrder: "asc" | "desc";
  onSearchChange: (value: string) => void;
  onCompletedFilterChange: (value: "all" | "completed" | "open") => void;
  onSortByChange: (value: SortBy) => void;
  onSortOrderChange: (value: "asc" | "desc") => void;
};

export default function TaskControls({
  search,
  completedFilter,
  sortBy,
  sortOrder,
  onSearchChange,
  onCompletedFilterChange,
  onSortByChange,
  onSortOrderChange,
}: Props) {
  return (
    <section className="section">
      <h2 className="section-title">Task Controls</h2>

      <div className="controls-row">
        <input
          className="input"
          placeholder="Search tasks"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
        />

        <select
          className="select"
          value={completedFilter}
          onChange={(e) =>
            onCompletedFilterChange(
              e.target.value as "all" | "completed" | "open"
            )
          }
        >
          <option value="all">All</option>
          <option value="open">Open</option>
          <option value="completed">Completed</option>
        </select>

        <select
          className="select"
          value={sortBy}
          onChange={(e) => onSortByChange(e.target.value as SortBy)}
        >
          <option value="created_at">Created Date</option>
          <option value="due_date">Due Date</option>
          <option value="priority">Priority</option>
          <option value="title">Title</option>
          <option value="updated_at">Updated Date</option>
        </select>

        <select
          className="select"
          value={sortOrder}
          onChange={(e) => onSortOrderChange(e.target.value as "asc" | "desc")}
        >
          <option value="desc">Descending</option>
          <option value="asc">Ascending</option>
        </select>
      </div>
    </section>
  );
}