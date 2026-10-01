import {
  GraduationCap,
  LockKeyhole,
  RefreshCcw,
  ShieldAlert,
  ShieldCheck,
  UserRound,
} from "lucide-react";
import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import Brand from "../../components/Brand";
import { useAuth } from "../../context/AuthContext";

const DEMO_ACCOUNTS = [
  {
    label: "Lecturer",
    description: "Create, encrypt and manage exams",
    email: "david@secureexam.com",
    demoRole: "lecturer",
    icon: GraduationCap,
    className: "lecturer",
  },
  {
    label: "Authorized Student",
    description: "Decrypt exams and submit encrypted answers",
    email: "alice@secureexam.com",
    demoRole: "authorized_student",
    icon: UserRound,
    className: "student",
  },
  {
    label: "Unauthorized Student",
    description: "See ciphertext without receiving the exam key",
    email: "eve@secureexam.com",
    demoRole: "unauthorized_student",
    icon: ShieldAlert,
    className: "unauthorized",
  },
];

export default function LoginPage() {
  const {
    user,
    login,
    demoLogin,
    startFreshDemo,
    hasDemoSession,
  } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [demoLoading, setDemoLoading] = useState(null);
  const [resettingDemo, setResettingDemo] = useState(false);

  if (user) {
    return <Navigate to={`/${user.role}`} replace />;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      const loggedInUser = await login(email, password);
      navigate(`/${loggedInUser.role}`, { replace: true });
    } catch (err) {
      setError(err.message || "Unable to sign in");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDemoLogin(account) {
    setError("");
    setDemoLoading(account.demoRole);

    try {
      const loggedInUser = await demoLogin(account.demoRole);
      navigate(`/${loggedInUser.role}`, { replace: true });
    } catch (err) {
      setError(err.message || "Unable to open the demo");
    } finally {
      setDemoLoading(null);
    }
  }

  async function handleFreshDemo() {
    setError("");
    setResettingDemo(true);
    try {
      await startFreshDemo();
    } finally {
      setResettingDemo(false);
    }
  }

  const busy = submitting || demoLoading !== null || resettingDemo;

  return (
    <div className="login-screen">
      <section className="login-hero">
        <Brand />

        <div className="hero-copy">
          <span className="eyebrow">SECURE EXAMINATION WORKFLOW</span>
          <h1>Protect every exam from creation to submission.</h1>
          <p>
            Symmetric Serpent/OFB encryption, public-key exam-key delivery,
            and Falcon-style digital signatures in one educational security portal.
          </p>
        </div>

        <div className="crypto-strip">
          <span><ShieldCheck size={18} /> Signed exams</span>
          <span><LockKeyhole size={18} /> Encrypted answers</span>
        </div>
      </section>

      <section className="login-panel">
        <form className="login-card" onSubmit={handleSubmit}>
          <div>
            <span className="eyebrow">WELCOME BACK</span>
            <h2>Sign in to SecureExam</h2>
            <p>Use your portal account to continue.</p>
          </div>

          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>

          {error && <div className="alert alert-error">{error}</div>}

          <button
            className="button button-primary button-full"
            disabled={busy}
          >
            {submitting ? "Signing in…" : "Secure sign in"}
          </button>

          <div className="demo-login-section">
            <div className="demo-login-heading">
              <strong>Try the live demo</strong>
              <span>Private browser sandbox</span>
            </div>

            {hasDemoSession && (
              <div className="demo-session-banner">
                <div>
                  <ShieldCheck size={17} />
                  <span>
                    <strong>Your demo sandbox is active</strong>
                    Switch roles without losing exams or submissions.
                  </span>
                </div>
                <button
                  type="button"
                  className="demo-reset-button"
                  onClick={handleFreshDemo}
                  disabled={busy}
                >
                  <RefreshCcw size={14} />
                  {resettingDemo ? "Resetting…" : "Start fresh"}
                </button>
              </div>
            )}

            <div className="demo-account-list">
              {DEMO_ACCOUNTS.map((account) => {
                const Icon = account.icon;
                const loading = demoLoading === account.demoRole;

                return (
                  <button
                    key={account.demoRole}
                    type="button"
                    className={`demo-account demo-account-${account.className}`}
                    onClick={() => handleDemoLogin(account)}
                    disabled={busy}
                  >
                    <div className="demo-account-icon"><Icon size={19} /></div>
                    <div className="demo-account-copy">
                      <strong>{account.label}</strong>
                      <span>{account.description}</span>
                      <small>{account.email}</small>
                    </div>
                    <div className="demo-account-action">
                      {loading ? "Opening…" : "Try"}
                    </div>
                  </button>
                );
              })}
            </div>

            <p className="demo-note">
              One-click demo login uses an isolated, temporary sandbox. No demo password is exposed in the browser.
            </p>
          </div>
        </form>
      </section>
    </div>
  );
}
