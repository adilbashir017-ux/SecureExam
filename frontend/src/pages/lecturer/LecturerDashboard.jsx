import { FileLock2, FilePlus2 } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiRequest } from "../../api/client";

export default function LecturerDashboard() {
  const [exams, setExams] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    apiRequest("/exams/").then(setExams).catch((err) => setError(err.message));
  }, []);

  return (
    <>
      <div className="page-heading">
        <div><span className="eyebrow">LECTURER PORTAL</span><h1>Exam management</h1></div>
        <Link className="button button-primary" to="/lecturer/exams/new"><FilePlus2 size={17} /> Create exam</Link>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      <div className="card-grid">
        {exams.map((exam) => (
          <article className="card exam-card" key={exam.id}>
            <div className="card-icon"><FileLock2 size={22} /></div>
            <span className={`badge ${exam.status === "published" ? "badge-green" : "badge-gray"}`}>{exam.status}</span>
            <h3>{exam.title}</h3>
            <p>{exam.course}</p>
            <Link className="button button-secondary" to={`/lecturer/exams/${exam.id}`}>Manage exam</Link>
          </article>
        ))}
      </div>
    </>
  );
}
