import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Signup.css";
import { registerUser } from "../services/authService";

function Signup() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [nameError, setNameError] = useState("");
  const [emailError, setEmailError] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [confirmPasswordError, setConfirmPasswordError] = useState("");

  const [loading, setLoading] = useState(false);

  const validateName = () => {
    if (!name.trim()) {
      setNameError("Please enter your name.");
      return false;
    }

    if (name.trim().length < 2) {
      setNameError("Name must be at least 2 characters long.");
      return false;
    }

    setNameError("");
    return true;
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

  const validateConfirmPassword = () => {
    if (!confirmPassword) {
      setConfirmPasswordError("Please confirm your password.");
      return false;
    }

    if (confirmPassword !== password) {
      setConfirmPasswordError("Passwords do not match.");
      return false;
    }

    setConfirmPasswordError("");
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const isNameValid = validateName();
    const isEmailValid = validateEmail();
    const isPasswordValid = validatePassword();
    const isConfirmPasswordValid = validateConfirmPassword();

    if (
      !isNameValid ||
      !isEmailValid ||
      !isPasswordValid ||
      !isConfirmPasswordValid
    ) {
      return;
    }

    try {
      setLoading(true);

      const response = await registerUser(
        name,
        email,
        password
      );

      console.log("Registration successful:", response);

      alert("Account created successfully!");
      navigate("/login");
    } catch (error) {
      console.error("Registration failed:", error);

      alert(
        " Registration Error: " +
       (error.message || "Unknown error")
     );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signup-container">
      <div className="signup-card">

        <h1>Create Account</h1>

        <p className="signup-subtitle">
          Create your account to get started
        </p>

        <form onSubmit={handleSubmit}>

          {/* Name */}
          <div className="form-group">
            <label htmlFor="name">Name</label>

            <input
              id="name"
              type="text"
              placeholder="Enter your name"
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                if (nameError) setNameError("");
              }}
              onBlur={validateName}
            />

            {nameError && (
              <p className="error-message">
                {nameError}
              </p>
            )}
          </div>

          {/* Email */}
          <div className="form-group">
            <label htmlFor="signup-email">Email</label>

            <input
              id="signup-email"
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (emailError) setEmailError("");
              }}
              onBlur={validateEmail}
            />

            {emailError && (
              <p className="error-message">
                {emailError}
              </p>
            )}
          </div>

          {/* Password */}
          <div className="form-group">
            <label htmlFor="signup-password">
              Password
            </label>

            <div className="password-container">
              <input
                id="signup-password"
                type={showPassword ? "text" : "password"}
                placeholder="Enter your password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (passwordError) setPasswordError("");
                }}
                onBlur={validatePassword}
              />

              <button
                type="button"
                className="password-toggle"
                onClick={() =>
                  setShowPassword(!showPassword)
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

          {/* Confirm Password */}
          <div className="form-group">
            <label htmlFor="confirm-password">
              Confirm Password
            </label>

            <div className="password-container">
              <input
                id="confirm-password"
                type={
                  showConfirmPassword
                    ? "text"
                    : "password"
                }
                placeholder="Confirm your password"
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                  if (confirmPasswordError) {
                    setConfirmPasswordError("");
                  }
                }}
                onBlur={validateConfirmPassword}
              />

              <button
                type="button"
                className="password-toggle"
                onClick={() =>
                  setShowConfirmPassword(
                    !showConfirmPassword
                  )
                }
              >
                {showConfirmPassword ? "🙈" : "👁️"}
              </button>
            </div>

            {confirmPasswordError && (
              <p className="error-message">
                {confirmPasswordError}
              </p>
            )}
          </div>

          <button
            type="submit"
            className="signup-button"
            disabled={loading}
          >
            {loading
              ? "Creating Account..."
              : "Create Account"}
          </button>

        </form>

        <p className="login-link">
          Already have an account?{" "}
          <a href="/login">Login</a>
        </p>

      </div>
    </div>
  );
}

export default Signup;
