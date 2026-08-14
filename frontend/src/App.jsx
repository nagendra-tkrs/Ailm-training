import Dashboard from "./pages/Dashboard";
import Signup from "./pages/Signup";
import { Routes, Route } from "react-router-dom";

import MainLayout from "./layouts/MainLayout";

import Home from "./pages/Home";
import About from "./pages/About";
import Contact from "./pages/Contact";
import Login from "./pages/Login";
import LeaveHistory from "./pages/LeaveHistory";

function App() {
  return (
    <Routes>
      {/* Pages with Header and Footer */}
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Home />} />
        <Route path="about" element={<About />} />
        <Route path="contact" element={<Contact />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/leave-history" element={<LeaveHistory />} />
      </Route>

      {/* Login page */}
      <Route path="/login" element={<Login />} />
      {/* Sign Up page */}
      <Route path="/signup" element={<Signup />} />
    </Routes>
  );
}

export default App;
