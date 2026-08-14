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

  // Pagination (client-side as backend does not provide paging)
  const [page, setPage] = useState(1);
  const pageSize = 8;

  // Edit state
  const [editing, setEditing] = useState(null);
  const [editPayload, setEditPayload] = useState({});
  const [submitting, setSubmitting] = useState(false);

  const fetchLeaves = async () => {
    try {
      setLoading(true);
      setError("");

      const token = localStorage.getItem("token");
      if (!token) {
        navigate("/login");
        return;
      }

      const data = await listMyLeaves(token);
      // API returns snake_case spec; normalize to camelCase for UI convenience
      const normalized = data.map((l) => ({
        id: l.id,
        leaveType: l.leave_type,
        startDate: l.start_date,
        endDate: l.end_date,
        leaveDays: l.leave_days,
        reason: l.reason,
        status: l.status.toLowerCase(),
        createdAt: l.created_at,
      }));

      setLeaves(normalized);
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
    fetchLeaves();
  }, []);

  const filteredLeaves = leaves.filter((l) => {
    if (statusFilter !== "All" && l.status !== statusFilter.toLowerCase()) return false;
    if (fromDate && l.startDate < fromDate) return false;
    if (toDate && l.endDate > toDate) return false;
    return true;
  });

  const totalPages = Math.max(1, Math.ceil(filteredLeaves.length / pageSize));

  const pageItems = filteredLeaves.slice((page - 1) * pageSize, page * pageSize);

  const startEdit = (leave) => {
    setEditing(leave);
    setEditPayload({
      leave_type: leave.leaveType,
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
      await fetchLeaves();
      cancelEdit();
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
      await fetchLeaves();
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
        ) : filteredLeaves.length === 0 ? (
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
                <option value="Casual Leave">Casual Leave</option>
                <option value="Sick Leave">Sick Leave</option>
                <option value="Earned Leave">Earned Leave</option>
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
