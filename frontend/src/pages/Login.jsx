import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";
import { loginUser } from "../services/authService";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const [emailError, setEmailError] = useState("");
  const [passwordError, setPasswordError] = useState("");

  // Loading state
  const [loading, setLoading] = useState(false);

  const handleEmailChange = (e) => {
    setEmail(e.target.value);

    if (emailError) {
      setEmailError("");
    }
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);

    if (passwordError) {
      setPasswordError("");
    }
  };

  const validateEmail = () => {
    if (!email.trim()) {
      setEmailError("Please enter your email address.");
      return false;
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(email)) {
      setEmailError("Please enter a valid email address.");
      return false;
    }

    setEmailError("");
    return true;
  };

  const validatePassword = () => {
    if (!password) {
      setPasswordError("Please enter your password.");
      return false;
    }

    if (password.length < 8) {
      setPasswordError(
        "Password must be at least 8 characters long."
      );
      return false;
    }

    if (!/[A-Z]/.test(password)) {
      setPasswordError(
        "Password must contain at least one uppercase letter."
      );
      return false;
    }

    if (!/[a-z]/.test(password)) {
      setPasswordError(
        "Password must contain at least one lowercase letter."
      );
      return false;
    }

    if (!/[0-9]/.test(password)) {
      setPasswordError(
        "Password must contain at least one number."
      );
      return false;
    }

    if (!/[!@#$%^&*(),.?":{}|<>_\-\\[\]/;'+=~`]/.test(password)) {
      setPasswordError(
        "Password must contain at least one special character."
      );
      return false;
    }

    setPasswordError("");
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const isEmailValid = validateEmail();
    const isPasswordValid = validatePassword();

    if (!isEmailValid || !isPasswordValid) {
      return;
    }

    try {
      // Start loading
      setLoading(true);

      const response = await loginUser(email, password);

      // Handle successful login
      console.log("Login successful:", response);

      // Get JWT from the login response
      const token =
        response?.token ||
        response?.accessToken ||
        response?.jwt ||
        response?.data?.token;

        if (!token) {
          throw new Error("JWT token was not returned by the server.");
      }

      // Store JWT for authenticated API requests
      localStorage.setItem("token", token);

      // Navigate to Employee Dashboard
      navigate("/dashboard");
    } catch (error) {
      // Handle API error
      console.error("Login failed:", error);
      alert("Login failed. Please check your email and password.");
    } finally {
      // Stop loading after success or error
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>Welcome Back</h1>

        <p className="login-subtitle">
          Please login to your account
        </p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email</label>

            <input
              id="email"
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={handleEmailChange}
              onBlur={validateEmail}
            />

            {emailError && (
              <p className="error-message">
                {emailError}
              </p>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>

            <div className="password-container">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="Enter your password"
                value={password}
                onChange={handlePasswordChange}
                onBlur={validatePassword}
              />

              <button
                type="button"
                className="password-toggle"
                onClick={() =>
                  setShowPassword(!showPassword)
                }
                aria-label={
                  showPassword
                    ? "Hide password"
                    : "Show password"
                }
              >
                {showPassword ? "🙈" : "👁️"}
              </button>
            </div>

            {passwordError && (
              <p className="error-message">
                {passwordError}
              </p>
            )}
          </div>

          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;
