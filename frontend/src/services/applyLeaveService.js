import { API_URL } from "./api";

export const applyLeave = async (
  leaveType,
  startDate,
  endDate,
  leaveDays,
  reason,
  token
) => {
  try {
    const response = await fetch(`${API_URL}/leave`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        leaveType,
        startDate,
        endDate,
        leaveDays,
        reason,
      }),
    });

    let data = {};

    try {
      data = await response.json();
    } catch {
      data = {};
    }

    // Authentication error
    if (response.status === 401 || response.status === 403) {
      throw new Error("AUTHENTICATION_ERROR");
    }

    // Other API errors - FastAPI often returns { detail: "message" }
    if (!response.ok) {
      const message = data.message || data.detail || "Failed to submit leave request";
      throw new Error(message);
    }

    return data;
  } catch (error) {
    if (
      error.message === "AUTHENTICATION_ERROR"
    ) {
      throw error;
    }

    throw new Error(
      error.message ||
        "Something went wrong while submitting the leave request."
    );
  }
};