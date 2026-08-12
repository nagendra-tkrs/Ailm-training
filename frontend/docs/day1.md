# React Project - Day 1 Documentation

## Project Overview

This project was created as part of the Day 1 React development tasks.

The goal of Day 1 was to set up a React application, configure React Router, create a clean project folder structure, build basic pages and reusable components, verify navigation, and push the completed project to GitHub.

## Technology Used

- React
- Vite
- JavaScript / JSX
- React Router
- CSS
- Node.js
- npm
- Git
- GitHub
- Visual Studio Code

## Day 1 Tasks Completed

### 1. Create React Project

Created a new React project using Vite.

The project runs successfully in the local development environment.

### 2. Install Required Dependencies

Installed the required project dependencies using npm.

React Router was also installed for application routing.

### 3. Configure React Router

Configured React Router to allow navigation between different pages without manually changing the HTML page.

The application includes routes for:

- `/` - Home
- `/about` - About
- `/contact` - Contact

### 4. Create Project Folder Structure

Created an organized project structure inside the `src` directory.

```text
src/
├── assets/
├── components/
├── hooks/
├── layouts/
├── pages/
├── services/
├── App.jsx
├── App.css
├── index.css
└── main.jsx
```

#### Folder Purpose

- `components/` - Reusable UI components.
- `pages/` - Application pages/screens.
- `services/` - API and external service logic.
- `hooks/` - Reusable React hooks and logic.
- `layouts/` - Common page layouts such as headers and footers.
- `assets/` - Images and other static assets.

### 5. Create Layout Component

Created a `MainLayout` component.

The layout provides a common structure for pages, including:

- Header
- Page content
- Footer

This avoids repeating the same layout code on every page.

### 6. Create Pages

Created the initial application pages:

- Home
- About
- Contact

Each page can be accessed through its configured route.

### 7. Create Reusable Components

Created reusable components that can be shared across multiple pages.

The component structure helps keep the application modular and easier to maintain.

### 8. Create Services Folder

Created the `services` folder to keep API/external service-related code separate from UI code.

This prepares the project for future backend/API integration.

### 9. Create Hooks Folder

Created the `hooks` folder for reusable React logic and custom hooks that may be added as the application grows.

### 10. Create Assets Folder

Created the `assets` folder for application images, icons, and other static resources.

### 11. Verify React Application

Verified that the React application runs successfully using the Vite development server.

Command used:

```bash
npm run dev
```

The application was successfully opened in the browser through the local development server.

### 12. Test Navigation

Tested navigation between the configured routes:

```text
/
 /about
 /contact
```

Confirmed that the pages load correctly through React Router.

### 13. Push Project to GitHub

The completed Day 1 project was committed and pushed to GitHub.

Git repository:

`lohith-bhogadula/my-react-app`

Branch:

`main`

## Final Project Structure

The project structure after Day 1 is organized approximately as follows:

```text
my-react-app/
├── node_modules/
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
│   │   └── Contact.jsx
│   ├── services/
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
└── vite.config.js
```

> Note: The exact files inside some folders may change as the project continues to grow.

## Application Flow

The basic React application flow is:

```text
index.html
    ↓
main.jsx
    ↓
App.jsx
    ↓
React Router
    ↓
Page
    ↓
Components / Layout
```

For example:

```text
Browser
   ↓
/about
   ↓
App.jsx
   ↓
React Router
   ↓
About.jsx
   ↓
MainLayout
   ↓
Header + Page Content + Footer
```

## Acceptance Criteria

### React Project Runs Successfully

- React project created successfully.
- Vite development server runs successfully.
- Application opens in the browser.

### Routing Is Configured

- React Router installed.
- Routes configured.
- Home, About, and Contact pages are accessible.
- Navigation between pages was tested.

### Folder Structure Is Created

The following folders were created:

- `components`
- `pages`
- `services`
- `hooks`
- `assets`
- `layouts`

### Code Pushed to Git

- Project initialized with Git.
- Changes committed.
- Project pushed to GitHub.
- Main branch used for the project.

## How to Run the Project

Clone the repository and open the project directory:

```bash
cd my-react-app
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the local URL displayed by Vite in the terminal.

## Day 1 Completion Status

| Task | Status |
|---|---|
| Create React Project | Completed |
| Install Dependencies | Completed |
| Configure React Router | Completed |
| Create Folder Structure | Completed |
| Create Layout Component | Completed |
| Create Pages | Completed |
| Create Components | Completed |
| Create Services | Completed |
| Create Hooks | Completed |
| Create Assets | Completed |
| Verify Application Runs | Completed |
| Test Navigation | Completed |
| Push to GitHub | Completed |

## Next Step

Day 1 established the basic React project structure and routing foundation.

The next development phase can build application functionality on top of this structure, including forms, validation, API integration, loading states, error handling, and additional pages.

---

**Project:** my-react-app  
**Development Phase:** Day 1  
**Status:** Completed
