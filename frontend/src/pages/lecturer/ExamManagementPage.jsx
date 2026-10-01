import { FlaskConical, KeyRound, LockKeyhole, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { apiRequest } from "../../api/client";

export default function ExamManagementPage() {
  const { examId } = useParams();
  const [exam, setExam] = useState(null);
  const [content, setContent] = useState("");
  const [submissions, setSubmissions] = useState([]);
  const [decrypted, setDecrypted] = useState({});
  const [securityDemo, setSecurityDemo] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function fetchExamData() {
    const examData = await apiRequest(`/exams/${examId}/management`);
    const submissionData = examData.status === "published"
      ? await apiRequest(`/exams/${examId}/submissions`)
      : [];

    return { examData, submissionData };
  }

  async function refreshPageData() {
    const { examData, submissionData } = await fetchExamData();
    setExam(examData);
    setSubmissions(submissionData);
  }

  useEffect(() => {
    let active = true;

    fetchExamData()
      .then(({ examData, submissionData }) => {
        if (!active) return;
        setExam(examData);
        setSubmissions(submissionData);
      })
      .catch((err) => {
        if (active) setError(err.message);
      });

    return () => {
      active = false;
    };
    // examId is the only route value that changes the requested resource.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [examId]);

  async function publish() {
    setError("");
    try {
      await apiRequest(`/exams/${examId}/publish`, {
        method: "POST",
        body: JSON.stringify({ exam_content: content }),
      });
      setMessage("Exam encrypted, signed and published successfully.");
      await refreshPageData();
    } catch (err) {
      setError(err.message);
    }
  }

  async function decryptSubmission(id) {
    try {
      const result = await apiRequest(
        `/exams/${examId}/submissions/${id}/decrypt`,
        { method: "POST" }
      );
      setDecrypted((current) => ({ ...current, [id]: result.decrypted_answer }));
    } catch (err) {
      setError(err.message);
    }
  }

  async function runDemo() {
    try {
      setSecurityDemo(await apiRequest(`/exams/${examId}/security-demo`));
    } catch (err) {
      setError(err.message);
    }
  }

  if (!exam) return <div>{error || "Loading exam…"}</div>;

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">EXAM MANAGEMENT</span>
          <h1>{exam.title}</h1>
          <p>{exam.course}</p>
        </div>
        <span className={`badge ${exam.status === "published" ? "badge-green" : "badge-gray"}`}>
          {exam.status}
        </span>
      </div>

      <div className="management-grid">
        <section className="card">
          <div className="section-title"><KeyRound size={20} /> Authorized students</div>
          <div className="id-chips">
            {exam.authorized_student_ids.map((id) => <span key={id}>ID {id}</span>)}
          </div>
        </section>

        <section className="card">
          <div className="section-title"><ShieldCheck size={20} /> Crypto profile</div>
          <p>Serpent-style / OFB · Kyber-style key delivery · Falcon-style signature</p>
        </section>
      </div>

      {exam.status === "draft" && (
        <section className="card">
          <div className="section-title"><LockKeyhole size={20} /> Encrypt & publish</div>
          <p>
            Plaintext is used only during this request. The database stores the encrypted exam,
            IV, signature and protected key packages.
          </p>
          <textarea
            rows="14"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Enter the final exam questions…"
          />
          <button
            className="button button-primary"
            onClick={publish}
            disabled={!content.trim()}
          >
            Encrypt & publish exam
          </button>
        </section>
      )}

      {exam.status === "published" && (
        <>
          <section className="card">
            <div className="section-title"><FlaskConical size={20} /> Security lab</div>
            <button className="button button-secondary" onClick={runDemo}>
              Run tampering verification
            </button>
            {securityDemo && (
              <div className="security-demo-result">
                <span>
                  Original signature: <strong>{securityDemo.original_signature_valid ? "VALID" : "INVALID"}</strong>
                </span>
                <span>
                  Tampered copy: <strong>{securityDemo.tampered_signature_valid ? "VALID" : "INVALID"}</strong>
                </span>
              </div>
            )}
          </section>

          <section className="card">
            <div className="section-title"><LockKeyhole size={20} /> Encrypted submissions</div>
            {submissions.length === 0 && <p>No submissions yet.</p>}
            <div className="submission-list">
              {submissions.map((submission) => (
                <article className="submission-item" key={submission.id}>
                  <div>
                    <strong>Student {submission.student_id}</strong>
                    <small>{new Date(submission.submitted_at).toLocaleString()}</small>
                  </div>
                  <pre className="ciphertext small">{submission.encrypted_answer_hex}</pre>
                  <button
                    className="button button-secondary"
                    onClick={() => decryptSubmission(submission.id)}
                  >
                    Decrypt submission
                  </button>
                  {decrypted[submission.id] && (
                    <pre className="decrypted-answer">{decrypted[submission.id]}</pre>
                  )}
                </article>
              ))}
            </div>
          </section>
        </>
      )}

      {message && <div className="alert alert-success">{message}</div>}
      {error && <div className="alert alert-error">{error}</div>}
    </>
  );
}
