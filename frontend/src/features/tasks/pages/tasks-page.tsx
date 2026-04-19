import { useQuery } from "@tanstack/react-query";
import { getTasks } from "../api";

export default function TasksPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["tasks"],
    queryFn: getTasks,
  });

  if (isLoading) {
    return <div>Tasks werden geladen...</div>;
  }

  if (isError) {
    return <div>Fehler beim Laden der Tasks.</div>;
  }

  return (
    <div>
      <h1>Meine Tasks</h1>

      {data && data.length === 0 && <p>Keine Tasks vorhanden.</p>}

      <ul>
        {data?.map((task) => (
          <li key={task.id}>
            <strong>{task.title}</strong>
            {task.description && <span> - {task.description}</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}