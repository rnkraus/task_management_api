import { useQuery } from "@tanstack/react-query";
import { getTasks } from "../api";

type CompletedFilter = "all" | "completed" | "open";
type SortBy = "title" | "created_at" | "priority" | "due_date";
type SortOrder = "asc" | "desc";

type UseTaskQueryParams = {
  search: string;
  completedFilter: CompletedFilter;
  sortBy: SortBy;
  sortOrder: SortOrder;
};

export function useTaskQuery({
  search,
  completedFilter,
  sortBy,
  sortOrder,
}: UseTaskQueryParams) {
  return useQuery({
    queryKey: ["tasks", search, completedFilter, sortBy, sortOrder],
    queryFn: () =>
      getTasks({
        search,
        completed:
          completedFilter === "all"
            ? undefined
            : completedFilter === "completed",
        sort_by: sortBy,
        order: sortOrder,
      }),
  });
}