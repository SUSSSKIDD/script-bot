const API_BASE = import.meta.env.DEV
  ? "/api"
  : "https://backend-script-bot.onrender.com";

async function request(path, options = {}) {
  const token = localStorage.getItem("token");
  const apiKey = localStorage.getItem("geminiApiKey");

  const headers = { ...options.headers };

  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (apiKey) headers["X-Gemini-Key"] = apiKey;

  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    window.location.href = "/#/login";
    return;
  }

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data.detail || data.message || "Request failed");
  }

  return data;
}

export const api = {
  login: (data) =>
    request("/auth/login", { method: "POST", body: JSON.stringify(data) }),
  register: (data) =>
    request("/auth/register", { method: "POST", body: JSON.stringify(data) }),
  generate: (data) =>
    request("/generate", { method: "POST", body: JSON.stringify(data) }),
  getHistory: () => request("/history"),
  getScripts: () => request("/scripts"),
  uploadScript: (file) => {
    const form = new FormData();
    form.append("file", file);
    return request("/scripts/upload", { method: "POST", body: form });
  },
  deleteScript: (filename) =>
    request(`/scripts/${encodeURIComponent(filename)}`, { method: "DELETE" }),
};
