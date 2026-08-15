const API_BASE_URL = "http://localhost:5000/api";

const handleAuthError = (response) => {
  if (response.status === 401 || response.status === 403) {
    throw new Error("AUTHENTICATION_ERROR");
  }
};

const parseError = async (response) => {
  try {
    const err = await response.json();
    const message = Array.isArray(err.detail)
      ? err.detail.map((d) => d.msg).join(", ")
      : err.detail || err.message || "REQUEST_FAILED";
    throw new Error(message);
  } catch (error) {
    if (error instanceof SyntaxError) {
      throw new Error("REQUEST_FAILED");
    }
    throw error;
  }
};

export const getProfile = async (token) => {
  const response = await fetch(`${API_BASE_URL}/profile`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  handleAuthError(response);

  if (!response.ok) {
    await parseError(response);
  }

  return response.json();
};

export const updateProfile = async (token, data) => {
  const response = await fetch(`${API_BASE_URL}/profile`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  handleAuthError(response);

  if (!response.ok) {
    await parseError(response);
  }

  return response.json();
};

export const changePassword = async (token, data) => {
  const response = await fetch(`${API_BASE_URL}/profile/password`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  handleAuthError(response);

  if (!response.ok) {
    await parseError(response);
  }

  return response.json();
};
