import { useEffect, useState } from "react";
import axios from "axios";
import { Case, EntityType, ModuleMetadata, UseCase } from "./types";
import { GraphView } from "./components/Graph/GraphView";
import { ModulePanel } from "./components/ModulePanel/ModulePanel";

const API = "http://localhost:8000/api";

const PURPOSE_OPTIONS: { value: UseCase; label: string }[] = [
  { value: "research", label: "General Research" },
  { value: "fraud_prevention", label: "Fraud Prevention" },
  { value: "due_diligence", label: "Due Diligence" },
  { value: "journalism", label: "Journalism" },
  { value: "security", label: "Security" },
];

function LegalDisclaimer({ onAccept }: { onAccept: () => void }) {
  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-lg max-w-lg w-full p-6 flex flex-col gap-4">
        <h2 className="text-xl font-bold text-yellow-400">Legal Notice</h2>
        <div className="text-sm text-gray-300 space-y-3">
          <p>
            <strong>Nexus OSINT</strong> is an investigative research tool for publicly available information.
            It is <strong>not</strong> a consumer reporting agency and may not be used as a substitute
            for a consumer report under the Fair Credit Reporting Act (FCRA).
          </p>
          <p>
            You may <strong>not</strong> use this tool to make decisions about a person's eligibility for:
            employment, housing, credit, insurance, or any other purpose covered by the FCRA.
          </p>
          <p>
            Use of this tool is subject to the Terms of Service of each data source.
            You are solely responsible for ensuring your use complies with applicable laws.
          </p>
        </div>
        <button
          onClick={onAccept}
          className="bg-yellow-500 hover:bg-yellow-400 text-black font-semibold rounded px-4 py-2 transition-colors"
        >
          I Understand — Continue
        </button>
      </div>
    </div>
  );
}

export default function App() {
  const [accepted, setAccepted] = useState(() => sessionStorage.getItem("disclaimer") === "1");
  const [modules, setModules] = useState<ModuleMetadata[]>([]);
  const [currentCase, setCurrentCase] = useState<Case | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showNewCase, setShowNewCase] = useState(false);
  const [newCaseName, setNewCaseName] = useState("");
  const [newCasePurpose, setNewCasePurpose] = useState<UseCase>("research");

  useEffect(() => {
    axios.get<ModuleMetadata[]>(`${API}/modules/`).then((r) => setModules(r.data));
  }, []);

  const handleAccept = () => {
    sessionStorage.setItem("disclaimer", "1");
    setAccepted(true);
  };

  const createCase = async () => {
    if (!newCaseName.trim()) return;
    const r = await axios.post<Case>(`${API}/cases/`, {
      name: newCaseName,
      declared_purpose: newCasePurpose,
    });
    setCurrentCase(r.data);
    setShowNewCase(false);
    setNewCaseName("");
  };

  const runModule = async (moduleName: string, entityType: EntityType, entityLabel: string) => {
    if (!currentCase) return;
    setLoading(true);
    setError(null);
    try {
      await axios.post(`${API}/modules/execute`, {
        case_id: currentCase.id,
        module_name: moduleName,
        entity_type: entityType,
        entity_label: entityLabel,
        session_id: currentCase.id,
      });
      const updated = await axios.get<Case>(`${API}/cases/${currentCase.id}`);
      setCurrentCase(updated.data);
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? "Execution failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-950 text-gray-100 min-h-screen flex flex-col font-mono">
      {!accepted && <LegalDisclaimer onAccept={handleAccept} />}

      {/* Header */}
      <header className="flex items-center justify-between px-4 py-2 border-b border-gray-800 bg-gray-900">
        <div className="flex items-center gap-2">
          <span className="text-blue-400 font-bold text-lg">NEXUS</span>
          <span className="text-gray-500 text-sm">OSINT</span>
        </div>
        <div className="flex items-center gap-3">
          {currentCase && (
            <span className="text-xs text-gray-400">
              Case: <span className="text-white">{currentCase.name}</span>
              <span className="ml-2 text-gray-600">({currentCase.declared_purpose})</span>
            </span>
          )}
          <button
            onClick={() => setShowNewCase(true)}
            className="text-xs bg-blue-800 hover:bg-blue-700 px-3 py-1 rounded transition-colors"
          >
            + New Case
          </button>
        </div>
      </header>

      {/* New Case Modal */}
      {showNewCase && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-40">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 w-full max-w-md flex flex-col gap-4">
            <h3 className="font-bold text-lg">New Investigation</h3>
            <input
              className="bg-gray-800 border border-gray-600 rounded px-3 py-2 text-sm"
              placeholder="Case name"
              value={newCaseName}
              onChange={(e) => setNewCaseName(e.target.value)}
            />
            <div className="flex flex-col gap-1">
              <label className="text-xs text-gray-400">Declared Purpose</label>
              <select
                className="bg-gray-800 border border-gray-600 rounded px-3 py-2 text-sm"
                value={newCasePurpose}
                onChange={(e) => setNewCasePurpose(e.target.value as UseCase)}
              >
                {PURPOSE_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
              <p className="text-[11px] text-gray-500 mt-1">
                Purpose determines which modules are available. Choose accurately.
              </p>
            </div>
            <div className="flex gap-2">
              <button onClick={createCase} className="bg-blue-700 hover:bg-blue-600 px-4 py-2 rounded text-sm flex-1 transition-colors">
                Create
              </button>
              <button onClick={() => setShowNewCase(false)} className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded text-sm transition-colors">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-72 border-r border-gray-800 bg-gray-900 flex flex-col overflow-hidden">
          <div className="px-3 py-2 border-b border-gray-800 text-xs text-gray-400 uppercase tracking-wide">
            Modules
          </div>
          {currentCase ? (
            <ModulePanel
              modules={modules}
              selectedEntityType={null}
              onExecute={runModule}
              loading={loading}
            />
          ) : (
            <div className="flex-1 flex items-center justify-center p-4">
              <p className="text-xs text-gray-500 text-center">
                Create a case to start an investigation.
              </p>
            </div>
          )}
        </aside>

        {/* Graph */}
        <main className="flex-1 relative bg-gray-950">
          {error && (
            <div className="absolute top-3 left-1/2 -translate-x-1/2 z-10 bg-red-900 border border-red-700 text-red-200 text-xs px-4 py-2 rounded">
              {error}
            </div>
          )}
          {currentCase && (currentCase.entities.length > 0) ? (
            <GraphView
              entities={currentCase.entities as never}
              relationships={currentCase.relationships as never}
            />
          ) : (
            <div className="flex items-center justify-center h-full text-gray-600 text-sm">
              {currentCase ? "Run a module to populate the graph." : "No active case."}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
