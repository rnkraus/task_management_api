export type LoginResponse = {
  access_token: string;
  token_type: string;
};

export type User = {
  id: number;
  email: string;
  name: string;
  role: string;
  created_at: string;
  updated_at: string;
};