import { useState } from "react";
import { ModuleMetadata, EntityType, Entity } from "../../types";

const TOS_BADGE: Record<string, string> = {
  none: "bg-green-700",
  low: "bg-yellow-600",
  medium: "bg-orange-600",
  high: "bg-red-700",
};

interface Props {
  modules: ModuleMetadata[];
  selectedEntityType: EntityType | null;
  onExecute: (moduleName: string, entityType: EntityType, entityLabel: string) => void;
  loading: boolean;
}

export function ModulePanel({ modules, selectedEntityType, onExecute, loading }: Props) {
  const [label, setLabel] = useState("");
  const [selectedType, setSelectedType] = useState<EntityType>("person");

  const available = modules.filter((m) =>
    m.input_types.includes(selectedEntityType ?? selectedType)
  );

  return (
    <div className="flex flex-col gap-3 p-3 overflow-y-auto h-full">
      <div className="flex flex-col gap-1">
        <label className="text-xs text-gray-400 uppercase tracking-wide">Entity Type</label>
        <select
          className="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm"
          value={selectedEntityType ?? selectedType}
          onChange={(e) => setSelectedType(e.target.value as EntityType)}
        >
          {["person","company","domain","email","username","ip","phone"].map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-xs text-gray-400 uppercase tracking-wide">Search Value</label>
        <input
          className="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm"
          placeholder="Name, domain, username…"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
        />
      </div>

      <div className="mt-2 flex flex-col gap-2">
        <p className="text-xs text-gray-400 uppercase tracking-wide">
          Available Modules ({available.length})
        </p>
        {available.map((m) => (
          <div key={m.name} className="bg-gray-800 rounded p-2 flex flex-col gap-1 border border-gray-700">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">{m.display_name}</span>
              <span className={`text-[10px] px-1.5 py-0.5 rounded ${TOS_BADGE[m.tos_risk]} text-white`}>
                T&S: {m.tos_risk}
              </span>
            </div>
            <p className="text-xs text-gray-400">{m.description}</p>
            {m.prohibited_uses.length > 0 && (
              <p className="text-[10px] text-red-400">
                Not for: {m.prohibited_uses.join(", ")}
              </p>
            )}
            <button
              disabled={!label.trim() || loading}
              onClick={() => onExecute(m.name, selectedEntityType ?? selectedType, label.trim())}
              className="mt-1 bg-blue-700 hover:bg-blue-600 disabled:opacity-40 text-xs rounded px-2 py-1 text-white transition-colors"
            >
              {loading ? "Running…" : "Run"}
            </button>
          </div>
        ))}
        {available.length === 0 && (
          <p className="text-xs text-gray-500 italic">No modules available for this entity type.</p>
        )}
      </div>
    </div>
  );
}
