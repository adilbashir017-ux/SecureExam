import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { apiRequest } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(
    () => Boolean(localStorage.getItem("secureexam_token"))
  );
  const [demoSessionToken, setDemoSessionToken] = useState(
    () => localStorage.getItem("secureexam_demo_session")
  );

  useEffect(() => {
    const token = localStorage.getItem("secureexam_token");
    if (!token) {
      return;
    }

    apiRequest("/auth/me")
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("secureexam_token");
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  async function login(email, password) {
    const data = await apiRequest("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });

    localStorage.setItem("secureexam_token", data.access_token);
    setUser(data.user);
    return data.user;
  }

  async function demoLogin(demoRole) {
    const data = await apiRequest("/auth/demo-login", {
      method: "POST",
      body: JSON.stringify({ demo_role: demoRole }),
    });

    if (data.demo_session_token) {
      localStorage.setItem("secureexam_demo_session", data.demo_session_token);
      setDemoSessionToken(data.demo_session_token);
    }

    localStorage.setItem("secureexam_token", data.access_token);
    setUser(data.user);
    return data.user;
  }

  function logout() {
    // Deliberately keep secureexam_demo_session so the same browser can
    // switch between Lecturer / Alice / Eve inside the same sandbox.
    localStorage.removeItem("secureexam_token");
    setUser(null);
  }

  async function startFreshDemo() {
    try {
      if (localStorage.getItem("secureexam_demo_session")) {
        await apiRequest("/auth/demo-reset", { method: "POST" });
      }
    } catch {
      // Even if the backend session already expired, clear the local token.
    } finally {
      localStorage.removeItem("secureexam_token");
      localStorage.removeItem("secureexam_demo_session");
      setDemoSessionToken(null);
      setUser(null);
    }
  }

  const value = useMemo(
    () => ({
      user,
      loading,
      login,
      demoLogin,
      logout,
      startFreshDemo,
      hasDemoSession: Boolean(demoSessionToken),
    }),
    [user, loading, demoSessionToken]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  return useContext(AuthContext);
}
