import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listMyLeaves, updateLeave, deleteLeave } from "../services/leavesService";
import "./LeaveHistory.css";

function LeaveHistory() {
  const navigate = useNavigate();
  const [leaves, setLeaves] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Filters
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");

  // Pagination (server-capable; fallback to client-side if backend doesn't support)
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(8);
  const [total, setTotal] = useState(0);

  // Edit state
  const [editing, setEditing] = useState(null);
  const [editPayload, setEditPayload] = useState({});
  const [submitting, setSubmitting] = useState(false);

  const fetchLeaves = async (requestedPage = page) => {
    try {
      setLoading(true);
      setError("");

      const token = localStorage.getItem("token");
      if (!token) {
        navigate("/login");
        return;
      }

      const params = {
        page: requestedPage,
        per_page: perPage,
        from_date: fromDate,
        to_date: toDate,
        status: statusFilter && statusFilter !== "All" ? statusFilter.toLowerCase() : undefined,
      };

      const data = await listMyLeaves(token, params);

      // data: { items: [...], total, page, per_page }
      const items = data.items || [];
      const normalized = items.map((l) => {
        const isSnake = !!l.leave_type || !!l.start_date;
        const rawType = isSnake ? l.leave_type : l.leaveType;
        const rawStatus = l.status || (l.status && l.status.toLowerCase());

        const statusRaw = l.status || l.status;

        return {
          id: l.id,
          leaveType: TOKEN_TO_DISPLAY[rawType] || rawType,
          startDate: isSnake ? l.start_date : l.startDate,
          endDate: isSnake ? l.end_date : l.endDate,
          leaveDays: isSnake ? l.leave_days : l.leaveDays,
          reason: l.reason,
          status: (statusRaw || "").toString().toLowerCase(),
          createdAt: isSnake ? l.created_at : l.createdAt,
        };
      });

      setLeaves(normalized);
      setTotal(data.total || normalized.length);
      setPage(data.page || requestedPage);
      setPerPage(data.per_page || perPage);

      return { items: normalized, total: data.total || normalized.length, page: data.page || requestedPage, per_page: data.per_page || perPage };
    } catch (err) {
      console.error(err);
      if (err.message === "AUTHENTICATION_ERROR") {
        localStorage.removeItem("token");
        navigate("/login");
        return;
      }
      setError("Failed to load leave history.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeaves(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fromDate, toDate, statusFilter, perPage]);

  useEffect(() => {
    fetchLeaves(page);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page]);

  const totalPages = Math.max(1, Math.ceil(total / perPage));
  const pageItems = leaves;

  const DISPLAY_TO_TOKEN = {
    "Casual Leave": "CASUAL",
    "Sick Leave": "SICK",
    "Earned Leave": "EARNED",
  };

  const TOKEN_TO_DISPLAY = {
    CASUAL: "Casual Leave",
    SICK: "Sick Leave",
    EARNED: "Earned Leave",
  };

  const startEdit = (leave) => {
    setEditing(leave);
    setEditPayload({
      leave_type: DISPLAY_TO_TOKEN[leave.leaveType] || leave.leaveType,
      start_date: leave.startDate,
      end_date: leave.endDate,
      reason: leave.reason,
    });
  };

  const cancelEdit = () => {
    setEditing(null);
    setEditPayload({});
  };

  const submitEdit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const token = localStorage.getItem("token");
      await updateLeave(editing.id, editPayload, token);
      alert("Leave updated successfully.");
      cancelEdit();
      // Refresh current page
      await fetchLeaves(page);
    } catch (err) {
      console.error(err);
      alert(err.message || "Failed to update leave");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (leave) => {
    if (!confirm("Are you sure you want to delete this pending leave request?")) return;
    try {
      const token = localStorage.getItem("token");
      await deleteLeave(leave.id, token);
      alert("Leave deleted successfully.");
      // After deletion, refresh. If current page becomes empty, go to previous page.
      const result = await fetchLeaves(page);
      if (result.items.length === 0 && page > 1) {
        setPage((p) => p - 1);
      }
    } catch (err) {
      console.error(err);
      alert(err.message || "Failed to delete leave");
    }
  };

  return (
    <div className="leave-history-page">
      <div className="container">
        <h1>Leave History</h1>

        {/* Filters */}
        <div className="filters">
          <div className="filter-item">
            <label>From</label>
            <input type="date" value={fromDate} onChange={(e)=>{setFromDate(e.target.value); setPage(1);}} />
          </div>
          <div className="filter-item">
            <label>To</label>
            <input type="date" value={toDate} onChange={(e)=>{setToDate(e.target.value); setPage(1);}} />
          </div>
          <div className="filter-item">
            <label>Status</label>
            <select value={statusFilter} onChange={(e)=>{setStatusFilter(e.target.value); setPage(1);}}>
              <option>All</option>
              <option>Pending</option>
              <option>Approved</option>
              <option>Rejected</option>
            </select>
          </div>
          <div className="filter-item actions">
            <button onClick={()=>{setFromDate(""); setToDate(""); setStatusFilter("All"); setPage(1);}}>Reset</button>
          </div>
        </div>

        {loading ? (
          <div className="loading">Loading...</div>
        ) : error ? (
          <div className="error">{error}</div>
        ) : leaves.length === 0 ? (
          <div className="empty">No leave records found.</div>
        ) : (
          <>
            <table className="leave-history-table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Start</th>
                  <th>End</th>
                  <th>Days</th>
                  <th>Reason</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {pageItems.map((l) => (
                  <tr key={l.id}>
                    <td>{l.leaveType}</td>
                    <td>{l.startDate}</td>
                    <td>{l.endDate}</td>
                    <td>{l.leaveDays}</td>
                    <td>{l.reason}</td>
                    <td className={`status ${l.status}`}>{l.status}</td>
                    <td>{l.createdAt}</td>
                    <td>
                      {l.status === "pending" && (
                        <>
                          <button className="btn-link" onClick={()=>startEdit(l)}>Edit</button>
                          <button className="btn-link danger" onClick={()=>handleDelete(l)}>Delete</button>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Pagination */}
            <div className="pagination">
              <button disabled={page<=1} onClick={()=>setPage(p=>Math.max(1,p-1))}>Prev</button>
              <span>Page {page} of {totalPages}</span>
              <button disabled={page>=totalPages} onClick={()=>setPage(p=>Math.min(totalPages,p+1))}>Next</button>
            </div>
          </>
        )}

        {/* Edit modal area */}
        {editing && (
          <div className="edit-modal">
            <form onSubmit={submitEdit} className="edit-form">
              <h3>Edit Leave</h3>
              <label>Leave Type</label>
              <select value={editPayload.leave_type} onChange={(e)=>setEditPayload({...editPayload, leave_type: e.target.value})}>
                <option value="CASUAL">Casual Leave</option>
                <option value="SICK">Sick Leave</option>
                <option value="EARNED">Earned Leave</option>
              </select>

              <label>Start Date</label>
              <input type="date" value={editPayload.start_date} onChange={(e)=>setEditPayload({...editPayload, start_date: e.target.value})} />

              <label>End Date</label>
              <input type="date" value={editPayload.end_date} onChange={(e)=>setEditPayload({...editPayload, end_date: e.target.value})} />

              <label>Reason</label>
              <textarea value={editPayload.reason} onChange={(e)=>setEditPayload({...editPayload, reason: e.target.value})} />

              <div className="modal-actions">
                <button type="button" onClick={cancelEdit}>Cancel</button>
                <button type="submit" disabled={submitting}>{submitting?"Saving...":"Save"}</button>
              </div>
            </form>
          </div>
        )}

      </div>
    </div>
  );
}

export default LeaveHistory;
