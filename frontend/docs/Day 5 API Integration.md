Day 5 — API Integration

This document summarizes the Day 5 API integration between the frontend and backend (Dashboard + Apply Leave).

1) Dashboard API endpoint used
- GET http://localhost:5000/api/employee/dashboard
- Backend route: [app/routes/dashboard.py](app/routes/dashboard.py#L1)

2) Apply Leave API endpoint used
- POST http://localhost:5000/api/leave
- Backend route: [app/routes/leaves.py](app/routes/leaves.py#L1)

3) Request method for each API
- Dashboard: GET
- Apply Leave: POST

4) Request body structure (Apply Leave)
- JSON body keys sent by frontend (from `src/services/applyLeaveService.js`):
  {
    "leaveType": "Casual Leave" | "Sick Leave" | "Earned Leave",
    "startDate": "YYYY-MM-DD",
    "endDate": "YYYY-MM-DD",
    "leaveDays": number,    // calculated client-side but server recalculates
    "reason": "string"
  }

5) Date format confirmed with backend
- Backend Pydantic model (`app/schemas/leave.py`) defines `startDate` and `endDate` as `date`.
- Pydantic accepts ISO date strings in the form `YYYY-MM-DD` (the frontend `<input type="date">` produces this format).
- Note: server recalculates leave days using `calculate_leave_days(startDate, endDate)` in `app/services/leave_service.py`.

6) JWT Authorization implementation confirmation
- Login endpoint returns `{ "access_token": "<token>", "token_type": "bearer" }` (`app/routes/auth.py`).
- Frontend stores token in `localStorage` (key: `token`) in `src/pages/Login.jsx`.
- Frontend includes header `Authorization: Bearer <token>` in `src/services/dashboardService.js` and `src/services/applyLeaveService.js`.
- Backend dependency `get_current_user` (`app/core/dependencies.py`) uses `HTTPBearer` and `jose.jwt.decode` to verify and extract `sub` (user id), `email`, and `role` from the token.

7) Dashboard API response mapping
- Backend `leave_service.get_dashboard_data` returns JSON with keys:
  {
    "leaveBalance": { "casual": int, "sick": int, "earned": int },
    "pendingLeaves": [ { "id", "leaveType", "startDate", "endDate", "days", "reason", "status", "createdDate" }, ... ],
    "approvedLeaves": [ same structure ]
  }
- Frontend `Dashboard.jsx` reads and maps these fields directly: `data.leaveBalance`, `data.pendingLeaves`, `data.approvedLeaves`.

8) Apply Leave API response handling
- On success, backend returns:
  {
    "message": "Leave request submitted successfully",
    "leave": { /* serialized leave object */ }
  }
- Frontend `applyLeave` (service) parses JSON and returns it to the caller (Dashboard). `Dashboard.jsx`:
  - Shows a success message (`Leave request submitted successfully.`),
  - Resets form fields,
  - Calls `fetchDashboardData()` to refresh `leaveBalance`, `pendingLeaves`, and `approvedLeaves`.
- Error handling:
  - Frontend treats HTTP 401/403 as `AUTHENTICATION_ERROR` and triggers logout + redirect to Login.
  - Other 4xx/5xx responses: frontend attempts to parse `data.detail` or `data.message` (FastAPI convention) and surfaces a friendly error message.

Notes / Implementation details
- Backend enforces date validation and recalculates duration server-side. Do not rely on `leaveDays` for server-side validation.
- Ensure CORS is enabled on backend when serving frontend from a different port (Vite default port 5173). Check `app/main.py` for `CORSMiddleware` configuration.

Where to verify in the codebase
- Frontend service files:
  - [frontend/src/services/dashboardService.js](src/services/dashboardService.js#L1)
  - [frontend/src/services/applyLeaveService.js](src/services/applyLeaveService.js#L1)
  - [frontend/src/services/authService.js](src/services/authService.js#L1)
- Frontend pages:
  - [frontend/src/pages/Dashboard.jsx](src/pages/Dashboard.jsx#L1)
  - [frontend/src/pages/Login.jsx](src/pages/Login.jsx#L1)
- Backend routes & schemas:
  - [backend/app/routes/dashboard.py](app/routes/dashboard.py#L1)
  - [backend/app/routes/leaves.py](app/routes/leaves.py#L1)
  - [backend/app/routes/auth.py](app/routes/auth.py#L1)
  - [backend/app/schemas/leave.py](app/schemas/leave.py#L1)

Generated on: 2026-08-13
