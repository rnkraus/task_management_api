import { useQuery } from "@tanstack/react-query";
import { getMe } from "../api";

export function useAuth() {
  const token = localStorage.getItem("access_token");

  const meQuery = useQuery({
    queryKey: ["me"],
    queryFn: getMe,
    enabled: !!token,
    retry: false,
  });

  return {
    token,
    user: meQuery.data ?? null,
    isLoading: meQuery.isLoading,
    isAuthenticated: !!token && !!meQuery.data,
    isError: meQuery.isError,
  };
}