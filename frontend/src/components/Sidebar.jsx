import { Link } from "react-router-dom";

function Sidebar() {
  return (
    <aside
      style={{
        width: "220px",
        minHeight: "100vh",
        backgroundColor: "#f4f4f4",
        padding: "20px",
      }}
    >
      <h3>Menu</h3>

      <nav>
        <p>
          <Link to="/">Home</Link>
        </p>

        <p>
          <Link to="/about">About</Link>
        </p>
      </nav>
    </aside>
  );
}

export default Sidebar;

