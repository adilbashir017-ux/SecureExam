import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiRequest } from "../../api/client";

export default function CreateExamPage() {
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [selected, setSelected] = useState([]);
  const [form, setForm] = useState({ title: "", course: "", duration_minutes: 120 });
  const [error, setError] = useState("");

  useEffect(() => {
    apiRequest("/users/students").then(setStudents).catch((err) => setError(err.message));
  }, []);

  function toggleStudent(id) {
    setSelected((current) => current.includes(id) ? current.filter((x) => x !== id) : [...current, id]);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      const exam = await apiRequest("/exams/", {
        method: "POST",
        body: JSON.stringify({ ...form, authorized_student_ids: selected }),
      });
      navigate(`/lecturer/exams/${exam.id}`);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="narrow-page">
      <div className="page-heading"><div><span className="eyebrow">NEW EXAM</span><h1>Create draft exam</h1></div></div>
      <form className="card form-card" onSubmit={handleSubmit}>
        <label>Title<input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required /></label>
        <label>Course<input value={form.course} onChange={(e) => setForm({ ...form, course: e.target.value })} required /></label>
        <label>Duration (minutes)<input type="number" min="1" value={form.duration_minutes} onChange={(e) => setForm({ ...form, duration_minutes: Number(e.target.value) })} required /></label>
        <div>
          <span className="form-label">Authorized students</span>
          <div className="student-selector">
            {students.map((student) => (
              <label className="student-option" key={student.id}>
                <input type="checkbox" checked={selected.includes(student.id)} onChange={() => toggleStudent(student.id)} />
                <span><strong>{student.full_name}</strong><small>{student.email} · ID {student.id}</small></span>
              </label>
            ))}
          </div>
        </div>
        {error && <div className="alert alert-error">{error}</div>}
        <button className="button button-primary" disabled={selected.length === 0}>Create draft</button>
      </form>
    </div>
  );
}
