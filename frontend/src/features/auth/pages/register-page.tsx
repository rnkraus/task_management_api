import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { register } from "../api";

export default function RegisterPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    if (!email.trim() || !name.trim() || !password.trim()) {
      setErrorMessage("All fields are required");
      return;
    }

    if (password.length < 8) {
      setErrorMessage("Password must be at least 8 characters");
      return;
    }

    try {
      setIsSubmitting(true);

      await register({
        email: email.trim(),
        name: name.trim(),
        password,
      });

      setSuccessMessage("Registration successful. Redirecting to login...");
      setTimeout(() => {
        navigate("/login");
      }, 1000);
    } catch (error: any) {
      const detail = error?.response?.data?.detail;

      if (typeof detail === "string") {
        setErrorMessage(detail);
      } else {
        setErrorMessage("Registration failed");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="page">
      <section className="section" style={{ maxWidth: "480px", margin: "0 auto" }}>
        <h1 className="page-title" style={{ marginBottom: "16px" }}>
          Register
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
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          <input
            className="input"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button className="button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Registering..." : "Register"}
          </button>
        </form>

        {errorMessage && <p className="error-text">{errorMessage}</p>}
        {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}

        <p className="muted-text" style={{ marginTop: "16px" }}>
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </section>
    </div>
  );
}