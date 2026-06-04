import { createContext, useContext, useEffect, useMemo, useState } from "react";

import api from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const bootstrapAuth = async () => {
    const token = localStorage.getItem("alp_token");
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const response = await api.get("/auth/me");
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem("alp_token");
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    bootstrapAuth();
  }, []);

  const login = async (payload) => {
    const response = await api.post("/auth/login", payload);
    localStorage.setItem("alp_token", response.data.access_token);
    setUser(response.data.user);
    return response.data;
  };

  const signup = async (payload) => {
    const response = await api.post("/auth/signup", payload);
    if (response.data?.access_token) {
      localStorage.setItem("alp_token", response.data.access_token);
      setUser(response.data.user);
    }
    return response.data;
  };

  const logout = () => {
    localStorage.removeItem("alp_token");
    setUser(null);
  };

  const value = useMemo(
    () => ({
      user,
      loading,
      login,
      signup,
      logout,
      isAuthenticated: Boolean(user),
    }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
