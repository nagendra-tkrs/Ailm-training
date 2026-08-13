import "../styles/layout.css";

function Footer() {
  return (
    <footer className="site-footer">
      <div>© {new Date().getFullYear()} Employee Leave Management</div>
    </footer>
  );
}

export default Footer;
