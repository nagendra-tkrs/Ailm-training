import Header from "../components/Header";
import Sidebar from "../components/Sidebar";
import Footer from "../components/Footer";
import { Outlet } from "react-router-dom";
import "../styles/layout.css";

function MainLayout() {
  return (
    <>
      <Header />

      <div style={{ display: "flex" }}>
        <Sidebar />

        <main className="main-content">
          <Outlet />
        </main>
      </div>

      <Footer />
    </>
  );
}

export default MainLayout;