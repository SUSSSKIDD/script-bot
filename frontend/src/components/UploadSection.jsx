import { useState, useEffect, useRef } from "react";
import { api } from "../api";

export default function UploadSection() {
  const [scripts, setScripts] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef();

  const fetchScripts = async () => {
    try {
      const data = await api.getScripts();
      setScripts(data.scripts || []);
    } catch {
      /* ignore */
    }
  };

  useEffect(() => {
    fetchScripts();
  }, []);

  const handleUpload = async () => {
    const file = fileRef.current?.files[0];
    if (!file) return;
    setError("");
    setUploading(true);
    try {
      await api.uploadScript(file);
      fileRef.current.value = "";
      await fetchScripts();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (filename) => {
    try {
      await api.deleteScript(filename);
      setScripts((prev) => prev.filter((s) => s.filename !== filename));
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <h3 className="text-sm font-medium text-gray-700 mb-2">
        Reference Scripts ({scripts.length})
      </h3>

      <div className="mb-2 space-y-2">
        <input
          ref={fileRef}
          type="file"
          accept=".pdf"
          className="w-full text-xs file:mr-2 file:py-1 file:px-2 file:rounded file:border-0 file:text-xs file:bg-blue-50 file:text-blue-700"
        />
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="w-full px-3 py-1.5 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {uploading ? "Uploading..." : "Upload PDF"}
        </button>
      </div>

      {error && <p className="text-xs text-red-600 mb-2">{error}</p>}

      {scripts.length > 0 && (
        <ul className="space-y-1 max-h-32 overflow-y-auto">
          {scripts.map((s) => (
            <li
              key={s.filename}
              className="flex items-center justify-between text-xs bg-gray-50 px-2 py-1 rounded"
            >
              <span className="truncate mr-2">{s.filename}</span>
              <button
                onClick={() => handleDelete(s.filename)}
                className="text-red-500 hover:text-red-700 shrink-0"
              >
                ✕
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
