import { Link } from "react-router-dom";
import "../styles/layout.css";

function Sidebar() {
  return (
    <aside className="site-sidebar">
      <h3>Navigation</h3>

      <nav>
        <Link to="/">Home</Link>
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/about">About</Link>
        <Link to="/contact">Contact</Link>
      </nav>
    </aside>
  );
}

export default Sidebar;

