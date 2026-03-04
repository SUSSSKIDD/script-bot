import { useAuth } from "../context/AuthContext";
import ApiKeyInput from "./ApiKeyInput";
import UploadSection from "./UploadSection";
import HistoryPanel from "./HistoryPanel";

export default function Sidebar({ onHistorySelect }) {
  const { user, logout } = useAuth();

  return (
    <aside className="w-72 bg-white border-r min-h-screen p-4 flex flex-col gap-6">
      <div>
        <h2 className="text-lg font-bold">Reels Script Bot</h2>
        <p className="text-sm text-gray-500 mt-1">Logged in as {user}</p>
      </div>

      <ApiKeyInput />
      <UploadSection />
      <HistoryPanel onSelect={onHistorySelect} />

      <div className="mt-auto">
        <button
          onClick={logout}
          className="w-full px-3 py-2 text-sm text-red-600 border border-red-200 rounded hover:bg-red-50"
        >
          Logout
        </button>
      </div>
    </aside>
  );
}
