import { useAuth } from "../context/AuthContext";

export default function ApiKeyInput() {
  const { apiKey, setApiKey } = useAuth();

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        Gemini API Key
      </label>
      <input
        type="password"
        value={apiKey}
        onChange={(e) => setApiKey(e.target.value)}
        placeholder="Optional override"
        className="w-full px-3 py-2 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      {apiKey && (
        <p className="text-xs text-green-600 mt-1">Using your API key</p>
      )}
    </div>
  );
}
