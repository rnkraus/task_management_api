import { Navigate } from "react-router-dom";
import { useAuth } from "../features/auth/hooks/use-auth";
import type { ReactNode } from "react";

type Props = {
  children: ReactNode;
};

export default function ProtectedRoute({ children }: Props) {
  const { token, isLoading, isAuthenticated } = useAuth();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    localStorage.removeItem("access_token");
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}