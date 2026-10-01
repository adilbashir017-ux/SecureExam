import { CheckCircle2, LockKeyhole, ShieldAlert, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { apiRequest } from "../../api/client";

export default function ExamPage() {
  const { examId } = useParams();
  const [exam, setExam] = useState(null);
  const [attempt, setAttempt] = useState(null);
  const [answer, setAnswer] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    apiRequest(`/exams/${examId}`).then(setExam).catch((err) => setError(err.message));
  }, [examId]);

  async function openExam() {
    setError("");
    try {
      setAttempt(await apiRequest(`/exams/${examId}/attempt`, { method: "POST" }));
    } catch (err) {
      setError(err.message);
    }
  }

  async function submitAnswer() {
    setError("");
    setMessage("");
    try {
      await apiRequest(`/exams/${examId}/submit`, {
        method: "POST",
        body: JSON.stringify({ answer_text: answer }),
      });
      setMessage("Your answer was encrypted and submitted successfully.");
    } catch (err) {
      setError(err.message);
    }
  }

  if (!exam) return <div>{error || "Loading exam…"}</div>;

  return (
    <>
      <div className="page-heading">
        <div><span className="eyebrow">SECURE EXAM</span><h1>{exam.title}</h1><p>{exam.course}</p></div>
        <span className="badge badge-blue">{exam.duration_minutes} min</span>
      </div>

      {!attempt && (
        <div className="card secure-open-card">
          <LockKeyhole size={30} />
          <h2>Open encrypted examination</h2>
          <p>The encrypted payload will be verified before any decryption is attempted.</p>
          <button className="button button-primary" onClick={openExam}>Verify & open exam</button>
        </div>
      )}

      {attempt && (
        <>
          <div className="security-status-grid">
            <Status label="Signature" ok={attempt.signature_valid} />
            <Status label="Exam key" ok={attempt.key_available} />
            <Status label="Decryption" ok={attempt.decryption_successful} />
          </div>
          {attempt.decryption_successful ? (
            <div className="card">
              <div className="section-title"><CheckCircle2 size={20} /> Decrypted examination</div>
              <pre className="exam-content">{attempt.exam_content}</pre>
              <label className="answer-label">Your answer<textarea rows="10" value={answer} onChange={(e) => setAnswer(e.target.value)} placeholder="Write your answer here…" /></label>
              <button className="button button-primary" onClick={submitAnswer} disabled={!answer.trim()}>Encrypt & submit answer</button>
            </div>
          ) : (
            <div className="card encrypted-card">
              <div className="section-title"><ShieldAlert size={20} /> Encrypted examination</div>
              <p>No protected exam key is available for your account, so the questions cannot be decrypted.</p>
              <pre className="ciphertext">{attempt.encrypted_content}</pre>
            </div>
          )}
        </>
      )}

      {message && <div className="alert alert-success">{message}</div>}
      {error && <div className="alert alert-error">{error}</div>}
    </>
  );
}

function Status({ label, ok }) {
  return (
    <div className={`security-status ${ok ? "ok" : "fail"}`}>
      {ok ? <ShieldCheck size={18} /> : <ShieldAlert size={18} />}
      <div><strong>{label}</strong><span>{ok ? "Verified" : "Unavailable"}</span></div>
    </div>
  );
}
