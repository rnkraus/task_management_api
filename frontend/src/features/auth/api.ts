import { api } from "../../lib/api-client";
import type { LoginResponse, User } from "./types";

export async function login(
  email: string,
  password: string
): Promise<LoginResponse> {
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", password);

  const res = await api.post("/auth/login", form, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });

  console.log("LOGIN RESPONSE:", res.data);

  return res.data;
}

export async function getMe(): Promise<User> {
  const res = await api.get("/users/me");
  console.log("GET ME RESPONSE:", res.data);
  return res.data;
}