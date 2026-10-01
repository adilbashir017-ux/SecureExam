import { FilePlus2, LayoutDashboard, LogOut, ShieldCheck, Users } from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import Brand from "../components/Brand";
import { useAuth } from "../context/AuthContext";

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const links = {
    student: [{ to: "/student", label: "Exams", icon: LayoutDashboard }],
    lecturer: [
      { to: "/lecturer", label: "Dashboard", icon: LayoutDashboard },
      { to: "/lecturer/exams/new", label: "Create Exam", icon: FilePlus2 },
    ],
    admin: [{ to: "/admin", label: "Administration", icon: Users }],
  }[user.role];

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Brand compact />
        <nav>
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end
              className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}
            >
              <Icon size={18} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-security">
          <ShieldCheck size={18} />
          <span>
            {user.is_demo
              ? "Private demo sandbox active"
              : "Cryptographic protection active"}
          </span>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="topbar-user">
            <div>
              <strong>{user.full_name}</strong>
              <span>{user.role}</span>
            </div>
            {user.is_demo && <span className="demo-pill">DEMO SANDBOX</span>}
          </div>

          <button className="button button-ghost" onClick={handleLogout}>
            <LogOut size={17} /> {user.is_demo ? "Switch demo role" : "Logout"}
          </button>
        </header>
        <div className="page-container"><Outlet /></div>
      </main>
    </div>
  );
}
