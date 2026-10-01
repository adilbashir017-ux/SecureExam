import { Clock3, FileLock2, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiRequest } from "../../api/client";

export default function StudentDashboard() {
  const [exams, setExams] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    apiRequest("/exams/").then(setExams).catch((err) => setError(err.message));
  }, []);

  return (
    <>
      <div className="page-heading">
        <div><span className="eyebrow">STUDENT PORTAL</span><h1>Published exams</h1></div>
        <div className="status-pill"><ShieldCheck size={16} /> Secure session</div>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      <div className="card-grid">
        {exams.map((exam) => (
          <article className="card exam-card" key={exam.id}>
            <div className="card-icon"><FileLock2 size={22} /></div>
            <span className="badge badge-blue">{exam.status}</span>
            <h3>{exam.title}</h3>
            <p>{exam.course}</p>
            <div className="meta-row"><Clock3 size={16} /> {exam.duration_minutes} minutes</div>
            <Link className="button button-primary" to={`/student/exams/${exam.id}`}>Open exam</Link>
          </article>
        ))}
      </div>
      {!error && exams.length === 0 && <div className="empty-state">No published exams are available.</div>}
    </>
  );
}
