const API_BASE_URL = "http://localhost:5000/api";

export const getDashboardData = async (token) => {
  const response = await fetch(`${API_BASE_URL}/employee/dashboard`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  if (response.status === 401) {
    throw new Error("AUTHENTICATION_ERROR");
  }

  if (!response.ok) {
    throw new Error("DASHBOARD_REQUEST_FAILED");
  }

  return response.json();
};
