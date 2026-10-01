import { useEffect, useState } from "react";
import { apiRequest } from "../../api/client";

export default function AdminDashboard() {
  const [users, setUsers] = useState([]);
  const [exams, setExams] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([apiRequest("/users/"), apiRequest("/exams/")])
      .then(([usersData, examsData]) => { setUsers(usersData); setExams(examsData); })
      .catch((err) => setError(err.message));
  }, []);

  return (
    <>
      <div className="page-heading"><div><span className="eyebrow">ADMIN</span><h1>System overview</h1></div></div>
      {error && <div className="alert alert-error">{error}</div>}
      <div className="stats-grid">
        <div className="stat-card"><span>Users</span><strong>{users.length}</strong></div>
        <div className="stat-card"><span>Exams</span><strong>{exams.length}</strong></div>
        <div className="stat-card"><span>Published</span><strong>{exams.filter((x) => x.status === "published").length}</strong></div>
      </div>
      <section className="card">
        <div className="section-title">Users</div>
        <div className="table-wrap"><table><thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Role</th></tr></thead><tbody>{users.map((user) => <tr key={user.id}><td>{user.id}</td><td>{user.full_name}</td><td>{user.email}</td><td>{user.role}</td></tr>)}</tbody></table></div>
      </section>
    </>
  );
}
