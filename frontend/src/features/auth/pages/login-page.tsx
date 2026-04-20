import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login } from "../api";

export default function LoginPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErrorMessage("");

    try {
      const data = await login(email, password);
      localStorage.setItem("access_token", data.access_token);
      navigate("/tasks");
    } catch (error: any) {
      const detail = error?.response?.data?.detail;

      if (typeof detail === "string") {
        setErrorMessage(detail);
      } else {
        setErrorMessage("Login failed");
      }
    }
  }

  return (
    <div className="page">
      <section className="section" style={{ maxWidth: "480px", margin: "0 auto" }}>
        <h1 className="page-title" style={{ marginBottom: "16px" }}>
          Login
        </h1>

        <form onSubmit={handleSubmit} className="form-grid">
          <input
            className="input"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <input
            className="input"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button className="button" type="submit">
            Login
          </button>
        </form>

        {errorMessage && <p className="error-text">{errorMessage}</p>}

        <p className="muted-text" style={{ marginTop: "16px" }}>
          Don&apos;t have an account? <Link to="/register">Register</Link>
        </p>
      </section>
    </div>
  );
}