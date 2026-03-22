"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface AuthUser {
  user_id: string;
  email: string;
  org_id: string;
  full_name: string;
  role: string;
  business_name: string;
  tier: string;
  email_verified: boolean;
}

interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  verifyOtp: (email: string, code: string) => Promise<void>;
  resendOtp: (email: string) => Promise<void>;
  requestPasswordReset: (email: string) => Promise<void>;
  confirmPasswordReset: (email: string, code: string, newPassword: string) => Promise<void>;
  setEmailVerified: () => void;
}

interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
  phone?: string;
  business_name?: string;
  business_type?: string;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  loading: true,
  login: async () => {},
  register: async () => {},
  logout: () => {},
  verifyOtp: async () => {},
  resendOtp: async () => {},
  requestPasswordReset: async () => {},
  confirmPasswordReset: async () => {},
  setEmailVerified: () => {},
});

const TOKEN_KEY = "sme_access_token";
const USER_KEY = "sme_user";

/** Decode JWT payload without verification (browser-side expiry check only). */
function parseJwtExp(token: string): number | null {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return typeof payload.exp === "number" ? payload.exp : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Hydrate from localStorage on mount — reject expired tokens
  useEffect(() => {
    try {
      const savedToken = localStorage.getItem(TOKEN_KEY);
      const savedUser = localStorage.getItem(USER_KEY);
      if (savedToken && savedUser) {
        const exp = parseJwtExp(savedToken);
        if (exp && exp * 1000 < Date.now()) {
          localStorage.removeItem(TOKEN_KEY);
          localStorage.removeItem(USER_KEY);
        } else {
          setToken(savedToken);
          setUser(JSON.parse(savedUser));
        }
      }
    } catch {
      // corrupted storage — ignore
    }
    setLoading(false);
  }, []);

  const saveSession = useCallback((t: string, u: AuthUser) => {
    setToken(t);
    setUser(u);
    localStorage.setItem(TOKEN_KEY, t);
    localStorage.setItem(USER_KEY, JSON.stringify(u));
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(body.detail || "Login failed");
    }
    const data = await res.json();
    saveSession(data.access_token, {
      user_id: data.user_id,
      email: data.email,
      org_id: data.org_id,
      full_name: data.full_name,
      role: data.role,
      business_name: data.business_name || "",
      tier: data.tier || "starter",
      email_verified: data.email_verified ?? false,
    });
  }, [saveSession]);

  const register = useCallback(async (payload: RegisterData) => {
    const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(body.detail || "Registration failed");
    }
    const data = await res.json();
    saveSession(data.access_token, {
      user_id: data.user_id,
      email: data.email,
      org_id: data.org_id,
      full_name: data.full_name,
      role: data.role,
      business_name: data.business_name || "",
      tier: data.tier || "starter",
      email_verified: data.email_verified ?? false,
    });
  }, [saveSession]);

  const verifyOtp = useCallback(async (email: string, code: string) => {
    const res = await fetch(`${API_BASE_URL}/api/auth/otp/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, code }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(body.detail || "Verification failed");
    }
  }, []);

  const resendOtp = useCallback(async (email: string) => {
    const res = await fetch(`${API_BASE_URL}/api/auth/otp/resend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(body.detail || "Failed to resend code");
    }
  }, []);

  const requestPasswordReset = useCallback(async (email: string) => {
    const res = await fetch(`${API_BASE_URL}/api/auth/password-reset/request`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(body.detail || "Failed to send reset code");
    }
  }, []);

  const confirmPasswordReset = useCallback(async (email: string, code: string, newPassword: string) => {
    const res = await fetch(`${API_BASE_URL}/api/auth/password-reset/confirm`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, code, new_password: newPassword }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(body.detail || "Password reset failed");
    }
  }, []);

  const setEmailVerified = useCallback(() => {
    if (user) {
      const updated = { ...user, email_verified: true };
      setUser(updated);
      localStorage.setItem(USER_KEY, JSON.stringify(updated));
    }
  }, [user]);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }, []);

  return (
    <AuthContext.Provider value={{
      user, token, loading, login, register, logout,
      verifyOtp, resendOtp, requestPasswordReset, confirmPasswordReset, setEmailVerified,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
