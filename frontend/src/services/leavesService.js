import { API_URL } from "./api";

export const listMyLeaves = async (token, params = {}) => {
  const url = new URL(`${API_URL}/leaves`);
  Object.keys(params || {}).forEach((k) => {
    if (params[k] !== undefined && params[k] !== null && params[k] !== "") {
      url.searchParams.append(k, params[k]);
    }
  });

  const res = await fetch(url.toString(), {
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

  const parsed = await res.json();

  // Normalize backend response to a consistent shape:
  // { items: [...], total: N, page: X, per_page: Y }
  if (Array.isArray(parsed)) {
    return { items: parsed, total: parsed.length, page: 1, per_page: parsed.length };
  }

  if (parsed.leaves && Array.isArray(parsed.leaves)) {
    // Admin-style response may include pagination metadata under `pagination`.
    if (parsed.pagination && typeof parsed.pagination === "object") {
      return {
        items: parsed.leaves,
        total: parsed.pagination.total_records ?? parsed.leaves.length,
        page: parsed.pagination.current_page ?? 1,
        per_page: parsed.pagination.page_size ?? parsed.leaves.length,
      };
    }

    return { items: parsed.leaves, total: parsed.leaves.length, page: 1, per_page: parsed.leaves.length };
  }

  // If backend already implements pagination, return as-is (with fallback keys)
  if (parsed.items && Array.isArray(parsed.items)) {
    return {
      items: parsed.items,
      total: parsed.total ?? parsed.count ?? parsed.items.length,
      page: parsed.page ?? parsed.current_page ?? 1,
      per_page: parsed.per_page ?? parsed.limit ?? parsed.items.length,
    };
  }

  // Unknown shape - return empty
  return { items: [], total: 0, page: 1, per_page: 0 };
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
