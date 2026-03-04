import { createContext, useContext, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => localStorage.getItem("username"));
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [apiKey, setApiKeyState] = useState(
    () => localStorage.getItem("geminiApiKey") || ""
  );

  const login = (username, tok) => {
    localStorage.setItem("username", username);
    localStorage.setItem("token", tok);
    setUser(username);
    setToken(tok);
  };

  const logout = () => {
    localStorage.removeItem("username");
    localStorage.removeItem("token");
    setUser(null);
    setToken(null);
  };

  const setApiKey = (key) => {
    if (key) {
      localStorage.setItem("geminiApiKey", key);
    } else {
      localStorage.removeItem("geminiApiKey");
    }
    setApiKeyState(key);
  };

  return (
    <AuthContext.Provider value={{ user, token, apiKey, setApiKey, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
