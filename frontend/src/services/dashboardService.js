const API_BASE_URL = "http://localhost:5000/api";

export const getDashboardData = async (token) => {
  const response = await fetch(`${API_BASE_URL}/employee/dashboard`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  if (response.status === 401 || response.status === 403) {
    throw new Error("AUTHENTICATION_ERROR");
  }

  if (!response.ok) {
    // Try to parse error detail
    try {
      const err = await response.json();
      throw new Error(err.message || err.detail || "DASHBOARD_REQUEST_FAILED");
    } catch {
      throw new Error("DASHBOARD_REQUEST_FAILED");
    }
  }

  return response.json();
};
