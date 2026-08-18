import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { getDashboardData } from "../services/dashboardService";
import { applyLeave } from "../services/applyLeaveService";
import "./Dashboard.css";

function Dashboard() {
  const navigate = useNavigate();

  // Dashboard state
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Apply Leave form state
  const [leaveType, setLeaveType] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [leaveDays, setLeaveDays] = useState(0);
  const [reason, setReason] = useState("");

  // Validation state
  const [formErrors, setFormErrors] = useState({});

  // Submission state
  const [submitting, setSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState("");
  const [submitError, setSubmitError] = useState("");

  // Refs for date inputs so calendar icons can focus them
  const startDateRef = useRef(null);
  const endDateRef = useRef(null);

  // Today's date as YYYY-MM-DD to restrict past dates
  const todayIso = new Date().toISOString().split("T")[0];

  // Fetch Dashboard Data
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError("");

      const token = localStorage.getItem("token");

      // Check JWT
      if (!token) {
        localStorage.removeItem("token");
        navigate("/login");
        return;
      }

      const data = await getDashboardData(token);

      setDashboardData(data);
    } catch (error) {
      console.error("Dashboard error:", error);

      // Handle authentication error
      if (
        error.message === "AUTHENTICATION_ERROR"
      ) {
        localStorage.removeItem("token");
        navigate("/login");
      } else {
        // Surface the real error message when available to aid debugging
        setError(error?.message || "Unable to load dashboard data.");
      }
    } finally {
      setLoading(false);
    }
  };
  const token = localStorage.getItem('token')

  // Load dashboard when page opens
  useEffect(() => {
    fetchDashboardData();
  }, [token]);

  // Automatically calculate leave days
  useEffect(() => {
    if (!startDate || !endDate) {
      setLeaveDays(0);
      return;
    }

    const start = new Date(startDate);
    const end = new Date(endDate);

    // End date cannot be before start date
    if (end < start) {
      setLeaveDays(0);
      return;
    }

    const differenceInTime =
      end.getTime() - start.getTime();

    const differenceInDays =
      Math.floor(
        differenceInTime /
          (1000 * 60 * 60 * 24)
      ) + 1;

    setLeaveDays(differenceInDays);
  }, [startDate, endDate]);

  // Dashboard data
  const leaveBalance =
    dashboardData?.leaveBalance || null;

  const pendingLeaves =
    dashboardData?.pendingLeaves || [];

  const approvedLeaves =
    dashboardData?.approvedLeaves || [];

  // Validate Apply Leave form
  const validateLeaveForm = () => {
    const errors = {};

    // Leave Type
    if (!leaveType) {
      errors.leaveType =
        "Please select a leave type.";
    }

    // Start Date
    if (!startDate) {
      errors.startDate =
        "Please select a start date.";
    }

    // End Date
    if (!endDate) {
      errors.endDate =
        "Please select an end date.";
    }

    // Date comparison
    if (startDate && endDate) {
      const start = new Date(startDate);
      const end = new Date(endDate);

      if (end < start) {
        errors.endDate =
          "End date cannot be earlier than start date.";
      }
    }

    // Leave days
    if (leaveDays <= 0) {
      errors.leaveDays =
        "Leave days must be valid.";
    }

    // Reason
    if (!reason.trim()) {
      errors.reason =
        "Please enter a reason for your leave.";
    }

    // Leave balance
    if (
      leaveType &&
      leaveDays > 0 &&
      leaveBalance
    ) {
      let availableBalance = 0;

      if (leaveType === "Casual Leave") {
        availableBalance =
          Number(leaveBalance.casual) || 0;
      } else if (leaveType === "Sick Leave") {
        availableBalance =
          Number(leaveBalance.sick) || 0;
      } else if (
        leaveType === "Earned Leave"
      ) {
        availableBalance =
          Number(leaveBalance.earned) || 0;
      }

      if (leaveDays > availableBalance) {
        errors.leaveDays =
          `Requested leave exceeds your available ${leaveType} balance.`;
      }
    }

    setFormErrors(errors);

    return Object.keys(errors).length === 0;
  };

  // Handle Apply Leave
  const handleApplyLeave = async (e) => {
    e.preventDefault();

    // Clear previous messages
    setSubmitMessage("");
    setSubmitError("");

    // Validate form
    const isValid = validateLeaveForm();

    if (!isValid) {
      return;
    }

    // Get JWT
    const token = localStorage.getItem("token");

    if (!token) {
      localStorage.removeItem("token");
      navigate("/login");
      return;
    }

    try {
      // Start submitting
      setSubmitting(true);

      const response = await applyLeave(
        leaveType,
        startDate,
        endDate,
        leaveDays,
        reason,
        token
      );

      console.log(
        "Leave request submitted:",
        response
      );

      // Success message
      setSubmitMessage(
        "Leave request submitted successfully."
      );

      // Reset form
      setLeaveType("");
      setStartDate("");
      setEndDate("");
      setLeaveDays(0);
      setReason("");
      setFormErrors({});

      // Refresh dashboard
      await fetchDashboardData();
    } catch (error) {
      console.error(
        "Apply leave error:",
        error
      );

      // Authentication error
      if (
        error.message ===
        "AUTHENTICATION_ERROR"
      ) {
        localStorage.removeItem("token");
        navigate("/login");
        return;
      }

      // User-friendly error
      setSubmitError(
        "Failed to submit leave request. Please try again."
      );
    } finally {
      // Stop submitting
      setSubmitting(false);
    }
  };

  // Dashboard loading state
  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-container">
          <div className="dashboard-loading">
            Loading dashboard...
          </div>
        </div>
      </div>
    );
  }

  // Dashboard error state
  if (error) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-container">
          <div className="dashboard-error">
            {error}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-container">

        {/* Dashboard Header */}
        <div className="dashboard-header">
          <h1>Employee Dashboard</h1>

          <p>
            Welcome to your employee dashboard
          </p>
        </div>


        {/* Leave Balance */}
        <section className="dashboard-section">
          <h2>Leave Balance</h2>

          {leaveBalance ? (
            <div className="leave-balance-grid">

              <div className="leave-balance-card">
                <h3>Casual Leave</h3>

                <p>
                  {leaveBalance.casual} Days
                </p>
              </div>

              <div className="leave-balance-card">
                <h3>Sick Leave</h3>

                <p>
                  {leaveBalance.sick} Days
                </p>
              </div>

              <div className="leave-balance-card">
                <h3>Earned Leave</h3>

                <p>
                  {leaveBalance.earned} Days
                </p>
              </div>

            </div>
          ) : (
            <p className="empty-state">
              Leave balance is currently unavailable.
            </p>
          )}
        </section>

        {/* Quick link to Leave History */}
        <div
          className="leave-history-quickcard"
          onClick={() => navigate('/leave-history')}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => { if (e.key === 'Enter') navigate('/leave-history'); }}
        >
          <div className="quickcard-top">
            <h3>Leave History</h3>
            <span className="badge">{pendingLeaves.length || 0}</span>
          </div>
          <p>View and manage your leave requests</p>
        </div>

        {/* Pending Leaves */}
        <section className="dashboard-section">
          <h2>Pending Leaves</h2>

          <div className="leave-table-container">
            <table className="leave-table">
              <thead>
                <tr>
                  <th>Leave Type</th>
                  <th>Start Date</th>
                  <th>End Date</th>
                  <th>Days</th>
                  <th>Reason</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {pendingLeaves.length > 0 ? (
                  pendingLeaves.map((leave) => (
                    <tr key={leave.id}>
                      <td>
                        {leave.leaveType}
                      </td>

                      <td>
                        {leave.startDate}
                      </td>

                      <td>
                        {leave.endDate}
                      </td>

                      <td>
                        {leave.days}
                      </td>

                      <td>
                        {leave.reason}
                      </td>

                      <td>
                        {leave.status}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td
                      colSpan="6"
                      className="empty-state"
                    >
                      No pending leave requests.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        {/* Approved Leaves */}
        <section className="dashboard-section">
          <h2>Approved Leaves</h2>

          <div className="leave-table-container">
            <table className="leave-table">
              <thead>
                <tr>
                  <th>Leave Type</th>
                  <th>Start Date</th>
                  <th>End Date</th>
                  <th>Days</th>
                  <th>Reason</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {approvedLeaves.length > 0 ? (
                  approvedLeaves.map((leave) => (
                    <tr key={leave.id}>
                      <td>
                        {leave.leaveType}
                      </td>

                      <td>
                        {leave.startDate}
                      </td>

                      <td>
                        {leave.endDate}
                      </td>

                      <td>
                        {leave.days}
                      </td>

                      <td>
                        {leave.reason}
                      </td>

                      <td>
                        {leave.status}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td
                      colSpan="6"
                      className="empty-state"
                    >
                      No approved leave requests.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        {/* Apply Leave */}
        <section className="dashboard-section apply-leave-section">

          <h2>Apply Leave</h2>

          {/* Success message */}
          {submitMessage && (
            <p className="success-message">
              {submitMessage}
            </p>
          )}

          {/* Error message */}
          {submitError && (
            <p className="form-error">
              {submitError}
            </p>
          )}

          <form
            className="leave-form"
            onSubmit={handleApplyLeave}
          >

            {/* Leave Type */}
            <div className="form-group">

              <label htmlFor="leaveType">
                Leave Type
              </label>

              <select
                id="leaveType"
                value={leaveType}
                onChange={(e) => {
                  setLeaveType(
                    e.target.value
                  );

                  if (formErrors.leaveType) {
                    setFormErrors((previous) => ({
                      ...previous,
                      leaveType: "",
                    }));
                  }
                }}
              >
                <option value="" disabled>
                  Select Leave Type
                </option>

                <option value="Casual Leave">
                  Casual Leave
                </option>

                <option value="Sick Leave">
                  Sick Leave
                </option>

                <option value="Earned Leave">
                  Earned Leave
                </option>
              </select>

              {formErrors.leaveType && (
                <p className="form-error">
                  {formErrors.leaveType}
                </p>
              )}

            </div>

            {/* Dates */}
            <div className="form-row">

              {/* Start Date */}
              <div className="form-group">

                <label htmlFor="startDate">
                  Start Date
                </label>

                <input
                  id="startDate"
                  type="date"
                  ref={startDateRef}
                  min={todayIso}
                  value={startDate}
                  onChange={(e) => {
                    setStartDate(
                      e.target.value
                    );

                    setSubmitMessage("");
                    setSubmitError("");
                  }}
                />

                <button
                  type="button"
                  className="date-icon"
                  aria-label="Open start date picker"
                  onClick={() => startDateRef.current && startDateRef.current.showPicker ? startDateRef.current.showPicker() : startDateRef.current && startDateRef.current.focus()}
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="3" y="5" width="18" height="16" rx="2" stroke="#444" strokeWidth="1.2"/>
                    <path d="M16 3V7M8 3V7" stroke="#444" strokeWidth="1.2" strokeLinecap="round"/>
                  </svg>
                </button>

                {formErrors.startDate && (
                  <p className="form-error">
                    {formErrors.startDate}
                  </p>
                )}

              </div>

              {/* End Date */}
              <div className="form-group">

                <label htmlFor="endDate">
                  End Date
                </label>

                <input
                  id="endDate"
                  type="date"
                  ref={endDateRef}
                  min={todayIso}
                  value={endDate}
                  onChange={(e) => {
                    setEndDate(
                      e.target.value
                    );

                    setSubmitMessage("");
                    setSubmitError("");
                  }}
                />

                <button
                  type="button"
                  className="date-icon"
                  aria-label="Open end date picker"
                  onClick={() => endDateRef.current && endDateRef.current.showPicker ? endDateRef.current.showPicker() : endDateRef.current && endDateRef.current.focus()}
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="3" y="5" width="18" height="16" rx="2" stroke="#444" strokeWidth="1.2"/>
                    <path d="M16 3V7M8 3V7" stroke="#444" strokeWidth="1.2" strokeLinecap="round"/>
                  </svg>
                </button>

                {formErrors.endDate && (
                  <p className="form-error">
                    {formErrors.endDate}
                  </p>
                )}

              </div>

            </div>

            {/* Leave Days */}
            <div className="form-group">

              <label htmlFor="leaveDays">
                Leave Days
              </label>

              <input
                id="leaveDays"
                type="text"
                value={leaveDays}
                readOnly
              />

              {formErrors.leaveDays && (
                <p className="form-error">
                  {formErrors.leaveDays}
                </p>
              )}

            </div>

            {/* Reason */}
            <div className="form-group">

              <label htmlFor="reason">
                Reason
              </label>

              <textarea
                id="reason"
                rows="4"
                placeholder="Enter the reason for your leave"
                value={reason}
                onChange={(e) => {
                  setReason(
                    e.target.value
                  );

                  if (formErrors.reason) {
                    setFormErrors((previous) => ({
                      ...previous,
                      reason: "",
                    }));
                  }
                }}
              ></textarea>

              {formErrors.reason && (
                <p className="form-error">
                  {formErrors.reason}
                </p>
              )}

            </div>

            {/* Apply Leave Button */}
            <button
              type="submit"
              className="apply-leave-button"
              disabled={submitting}
            >
              {submitting
                ? "Submitting..."
                : "Apply Leave"}
            </button>

          </form>

        </section>

      </div>
    </div>
  );
}

export default Dashboard;
