import { useState } from "react";

const FIELDS = [
  { key: "name", label: "Person's Name", placeholder: "e.g. Rahul" },
  { key: "college", label: "Masters College", placeholder: "e.g. UC Irvine" },
  { key: "field", label: "Field of Study", placeholder: "e.g. Computer Science" },
  { key: "situation", label: "Current Situation", placeholder: "e.g. Completed MS, working at Google" },
  { key: "topic", label: "Topic / Title", placeholder: "e.g. How I got into UC Irvine for MS in CS", full: true },
];

const empty = { name: "", college: "", field: "", situation: "", topic: "" };

export default function ScriptForm({ onGenerate, loading, initialValues }) {
  const [form, setForm] = useState(initialValues || empty);

  const set = (key, val) => setForm((prev) => ({ ...prev, [key]: val }));

  const handleSubmit = (e) => {
    e.preventDefault();
    onGenerate(form);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
        {FIELDS.map((f) => (
          <div key={f.key} className={f.full ? "sm:col-span-2" : ""}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {f.label}
            </label>
            <input
              type="text"
              value={form[f.key]}
              onChange={(e) => set(f.key, e.target.value)}
              placeholder={f.placeholder}
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
        ))}
      </div>
      <button
        type="submit"
        disabled={loading}
        className="w-full sm:w-auto px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? "Generating..." : "Generate Script"}
      </button>
    </form>
  );
}
