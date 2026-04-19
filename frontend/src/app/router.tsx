import { createBrowserRouter, Navigate } from "react-router-dom";

import LoginPage from "../features/auth/pages/login-page";
import TasksPage from "../features/tasks/pages/tasks-page";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to="/login" replace />,
  },
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/tasks",
    element: <TasksPage />,
  },
]);