# React Project - Day 2 Documentation

## Project Overview

Day 2 focused on building a professional frontend authentication flow for the React application created during Day 1.

The main goal was to create a responsive Login page and extend the authentication experience with a Create Account (Sign Up) page. The frontend is structured to communicate with a real backend API being developed separately.

> **Backend status:** Backend API development is being handled separately by a colleague. Real API integration and end-to-end authentication testing will be completed once the backend is available.

## Day 2 Features

- Login page
- Create Account / Sign Up page
- Email validation
- Password validation
- Confirm Password validation
- Password visibility controls
- Loading states
- API service layer
- Login API integration structure
- Registration API integration structure
- `/login` route
- `/signup` route
- Login ↔ Sign Up navigation
- Responsive design
- Git/GitHub version control

## Authentication Architecture

```text
React Frontend
      |
      +----------------------+
      |                      |
      v                      v
   /login                 /signup
      |                      |
      v                      v
 Login.jsx               Signup.jsx
      |                      |
      +----------+-----------+
                 |
                 v
          authService.js
                 |
                 v
           Backend API
                 |
                 v
              Database
```

The frontend does **not** store passwords in browser storage and does **not** use fake authentication. The backend will be integrated when the backend API is available.

---

# Day 2 Tasks

## Login

### 1. Create Login Page
Created:

```text
src/pages/Login.jsx
```

### 2. Design Login UI
Added email, password, login button, validation messages, loading state, and password visibility control.

### 3. Add Email Input
Added email input connected to React state.

### 4. Add Password Input
Added password input with show/hide functionality.

### 5. Email Validation
Added client-side email format validation.

### 6. Password Validation
Added client-side password validation.

### 7. Form Validation & Error Handling
Added validation and appropriate error messages before API submission.

### 8. Create Login API Service
Created:

```text
src/services/authService.js
```

The service is structured for:

```text
POST /api/login
```

### 9. Connect Login Form to API
Connected the Login form to `loginUser()`.

### 10. Handle Login API Success
Added frontend handling for successful API responses.

### 11. Handle Login API Errors
Added frontend handling for failed API requests.

### 12. Add Login Loading State
Added loading feedback such as:

```text
Logging in...
```

### 13. Configure `/login` Route
Configured the Login page through React Router.

### 14. Test Login Functionality
Tested rendering, validation, loading, API request behavior, and error handling.

Real authentication testing remains pending because the backend is not currently available.

### 15. Make Login Page Responsive
Created:

```text
src/pages/Login.css
```

with responsive desktop, tablet, and mobile styling.

---

# Create Account / Sign Up

The Create Account feature was added as an extension to the Day 2 authentication work.

### 16. Create Sign Up Page
Created:

```text
src/pages/Signup.jsx
```

### 17. Design Sign Up UI
Added:

- Name
- Email
- Password
- Confirm Password
- Password visibility controls
- Create Account button
- Validation messages
- Loading state
- Login navigation

### 18. Add Name Field
Added name input and validation.

### 19. Add Email Field
Added email input and client-side format validation.

### 20. Add Password Field
Added password validation requiring:

- Minimum 8 characters
- One uppercase letter
- One lowercase letter
- One number
- One special character

### 21. Add Confirm Password
Added validation to ensure the password and confirmation match.

### 22. Create Registration API Service
Extended:

```text
src/services/authService.js
```

with:

```text
registerUser()
```

The service is structured for:

```text
POST /api/register
```

No localStorage or fake authentication is used.

### 23. Configure `/signup` Route
Configured:

```text
/signup
```

through React Router.

### 24. Connect Login ↔ Sign Up Navigation
Added navigation between `/login` and `/signup`.

Flow:

```text
Login
  |
  | Don't have an account?
  v
Create Account
  |
  | Already have an account?
  v
Login
```

### 25. Test Sign Up Frontend Functionality
Tested:

- Page rendering
- Name validation
- Email validation
- Password validation
- Confirm Password validation
- Password visibility
- Loading state
- Form submission behavior

The frontend reaches the registration API request, but currently returns:

```text
Registration Error: Failed to fetch
```

A connectivity test to:

```text
http://localhost:5000
```

confirmed that no backend server is currently available on port 5000.

Therefore, real API registration testing is **pending backend availability**.

### 26. Make Sign Up Page Responsive
Created:

```text
src/pages/Signup.css
```

with responsive desktop, tablet, and mobile styling.

### 27. Update Day 2 Documentation
Updated this documentation to include the Login and Sign Up frontend work and the current backend dependency.

### 28. Push Day 2 Changes to GitHub
All completed frontend changes are ready to be committed and pushed.

---

# Backend Integration Plan

When the backend is available, we will confirm:

### Registration

```text
POST /api/register
```

Conceptual request:

```json
{
  "name": "User Name",
  "email": "user@example.com",
  "password": "Password@123"
}
```

### Login

```text
POST /api/login
```

The exact request and response formats will be based on the backend API contract provided by the backend developer.

Future integration testing will include:

1. Successful registration
2. Duplicate email handling
3. Successful login
4. Invalid credentials
5. Backend/network errors
6. Authentication/session handling if implemented

---

# Project Structure

```text
my-react-app/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   ├── hooks/
│   ├── layouts/
│   │   └── MainLayout.jsx
│   ├── pages/
│   │   ├── Home.jsx
│   │   ├── About.jsx
│   │   ├── Contact.jsx
│   │   ├── Login.jsx
│   │   ├── Login.css
│   │   ├── Signup.jsx
│   │   └── Signup.css
│   ├── services/
│   │   └── authService.js
│   ├── App.jsx
│   ├── App.css
│   ├── index.css
│   └── main.jsx
├── .gitignore
├── eslint.config.js
├── index.html
├── package.json
├── package-lock.json
├── README.md
├── day2.md
└── vite.config.js
```

---

# Testing Status

| Area | Status |
|---|---|
| Login UI | Completed |
| Login validation | Completed |
| Login loading state | Completed |
| Login API service | Completed |
| Login route | Completed |
| Login responsive design | Completed |
| Sign Up UI | Completed |
| Sign Up validation | Completed |
| Confirm Password validation | Completed |
| Sign Up loading state | Completed |
| Sign Up API service | Completed |
| Sign Up route | Completed |
| Login ↔ Sign Up navigation | Completed |
| Frontend testing | Completed |
| Real backend API testing | Pending backend availability |
| End-to-end authentication testing | Pending backend availability |
| GitHub push | Pending |

---

# How to Run

```bash
cd my-react-app
npm install
npm run dev
```

Login:

```text
http://localhost:5173/login
```

Create Account:

```text
http://localhost:5173/signup
```

---

# Day 2 Completion Checklist

| Subtask | Status |
|---|---|
| Create Login Page | Completed |
| Design Login UI | Completed |
| Add Email Input | Completed |
| Add Password Input | Completed |
| Email Validation | Completed |
| Password Validation | Completed |
| Form Validation & Error Handling | Completed |
| Create Login API Service | Completed |
| Connect Login Form to API | Completed |
| Handle Login API Success | Completed |
| Handle Login API Errors | Completed |
| Add Login Loading State | Completed |
| Configure `/login` Route | Completed |
| Test Login Functionality | Completed - frontend |
| Make Login Page Responsive | Completed |
| Create Sign Up Page | Completed |
| Design Sign Up UI | Completed |
| Add Name, Email & Password Fields | Completed |
| Add Confirm Password | Completed |
| Add Sign Up Validation | Completed |
| Create Registration API Service | Completed |
| Configure `/signup` Route | Completed |
| Connect Login ↔ Sign Up Navigation | Completed |
| Test Sign Up Functionality | Completed - frontend |
| Make Sign Up Responsive | Completed |
| Update Day 2 Documentation | Completed |
| Push Day 2 Changes to GitHub | Pending |

---

# Day 2 Result

The React frontend now contains a professional authentication interface with Login and Create Account flows.

The frontend is ready to connect to the real backend once backend development is complete.

**Project:** my-react-app  
**Development Phase:** Day 2  
**Frontend Status:** Completed  
**Backend Integration:** Pending backend availability  
**GitHub Status:** Ready to commit and push

## Next Development Phase

After these changes are committed and pushed to GitHub, the project can move to **Day 3**.
