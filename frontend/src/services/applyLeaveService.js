const API_URL = "http://localhost:5000/api";

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
    if (
      response.status === 401 ||
      response.status === 403
    ) {
      throw new Error("AUTHENTICATION_ERROR");
    }

    // Other API errors
    if (!response.ok) {
      throw new Error(
        data.message ||
          "Failed to submit leave request"
      );
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