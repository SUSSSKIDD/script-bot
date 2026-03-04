import { useState } from "react";
import { api } from "../api";
import Sidebar from "../components/Sidebar";
import ScriptForm from "../components/ScriptForm";
import ScriptOutput from "../components/ScriptOutput";

export default function GeneratorPage() {
  const [script, setScript] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastInputs, setLastInputs] = useState(null);

  const handleGenerate = async (inputs) => {
    setError("");
    setScript("");
    setLoading(true);
    setLastInputs(inputs);
    try {
      const data = await api.generate(inputs);
      if (data.script.startsWith("Error")) {
        setError(data.script);
      } else {
        setScript(data.script);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerate = () => {
    if (lastInputs) handleGenerate(lastInputs);
  };

  const handleHistorySelect = (entry) => {
    setScript(entry.script);
    setLastInputs(entry.inputs);
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar onHistorySelect={handleHistorySelect} />

      <main className="flex-1 p-8 max-w-4xl">
        <h1 className="text-2xl font-bold mb-6">Generate Reels Script</h1>

        <ScriptForm
          onGenerate={handleGenerate}
          loading={loading}
          initialValues={lastInputs}
        />

        {error && (
          <div className="mt-4 p-3 bg-red-50 text-red-700 rounded text-sm">
            {error}
          </div>
        )}

        <ScriptOutput
          script={script}
          onRegenerate={handleRegenerate}
          loading={loading}
        />
      </main>
    </div>
  );
}
