import "../styles/layout.css";

function Header() {
  return (
    <header className="site-header">
      <div className="site-brand">
        <div className="logo" aria-hidden="true"></div>
        <h3>Employee Leave</h3>
      </div>

      <nav className="site-nav">
        <a href="/dashboard">Dashboard</a>
        <a href="/profile">Profile</a>
      </nav>
    </header>
  );
}

export default Header;
