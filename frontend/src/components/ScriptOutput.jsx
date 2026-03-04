import { useState } from "react";

export default function ScriptOutput({ script, onRegenerate, loading }) {
  const [copied, setCopied] = useState(false);

  if (!script) return null;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(script);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const sections = script.split(/\n(?=(?:Hook|Intro|Problem|Solution):)/gi);

  return (
    <div className="mt-6 bg-white border rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Generated Script</h2>
        <div className="flex gap-2">
          <button
            onClick={handleCopy}
            className="px-3 py-1 text-sm border rounded hover:bg-gray-50"
          >
            {copied ? "Copied!" : "Copy"}
          </button>
          <button
            onClick={onRegenerate}
            disabled={loading}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "..." : "Regenerate"}
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {sections.map((section, i) => {
          const match = section.match(/^(Hook|Intro|Problem|Solution):\s*/i);
          if (match) {
            return (
              <div key={i}>
                <h3 className="font-semibold text-blue-700 mb-1">
                  {match[1]}
                </h3>
                <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">
                  {section.slice(match[0].length).trim()}
                </p>
              </div>
            );
          }
          return (
            <p key={i} className="text-gray-800 whitespace-pre-wrap leading-relaxed">
              {section.trim()}
            </p>
          );
        })}
      </div>
    </div>
  );
}
