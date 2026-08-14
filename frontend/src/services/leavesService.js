const API_URL = "http://localhost:5000/api";

export const listMyLeaves = async (token) => {
  const res = await fetch(`${API_URL}/leaves`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  if (res.status === 401 || res.status === 403) {
    throw new Error("AUTHENTICATION_ERROR");
  }

  if (!res.ok) {
    try {
      const err = await res.json();
      throw new Error(err.detail || err.message || "LIST_LEAVES_FAILED");
    } catch {
      throw new Error("LIST_LEAVES_FAILED");
    }
  }

  return res.json();
};

export const updateLeave = async (leaveId, payload, token) => {
  const res = await fetch(`${API_URL}/leaves/${leaveId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  if (res.status === 401 || res.status === 403) {
    throw new Error("AUTHENTICATION_ERROR");
  }

  if (!res.ok) {
    try {
      const err = await res.json();
      throw new Error(err.detail || err.message || "UPDATE_LEAVE_FAILED");
    } catch {
      throw new Error("UPDATE_LEAVE_FAILED");
    }
  }

  return res.json();
};

export const deleteLeave = async (leaveId, token) => {
  const res = await fetch(`${API_URL}/leaves/${leaveId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (res.status === 401 || res.status === 403) {
    throw new Error("AUTHENTICATION_ERROR");
  }

  if (!res.ok) {
    try {
      const err = await res.json();
      throw new Error(err.detail || err.message || "DELETE_LEAVE_FAILED");
    } catch {
      throw new Error("DELETE_LEAVE_FAILED");
    }
  }

  return res.json();
};

export default {
  listMyLeaves,
  updateLeave,
  deleteLeave,
};
