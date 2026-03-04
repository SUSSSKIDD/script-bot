import { useState, useEffect } from "react";
import { api } from "../api";

export default function HistoryPanel({ onSelect }) {
  const [entries, setEntries] = useState([]);
  const [open, setOpen] = useState(false);

  const fetchHistory = async () => {
    try {
      const data = await api.getHistory();
      setEntries(data.entries || []);
    } catch {
      /* ignore */
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  return (
    <div>
      <button
        onClick={() => {
          setOpen(!open);
          if (!open) fetchHistory();
        }}
        className="w-full text-left text-sm font-medium text-gray-700 flex items-center justify-between"
      >
        History ({entries.length})
        <span className="text-xs">{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <ul className="mt-2 space-y-1 max-h-48 overflow-y-auto">
          {entries.length === 0 && (
            <li className="text-xs text-gray-400">No history yet</li>
          )}
          {entries.map((e) => (
            <li key={e.id}>
              <button
                onClick={() => onSelect(e)}
                className="w-full text-left text-xs bg-gray-50 px-2 py-1.5 rounded hover:bg-gray-100"
              >
                <span className="font-medium">{e.inputs.topic || "Untitled"}</span>
                <span className="block text-gray-400">
                  {new Date(e.timestamp).toLocaleDateString()}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
