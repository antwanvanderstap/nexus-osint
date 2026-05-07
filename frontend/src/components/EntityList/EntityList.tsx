import { Entity, EntityType } from "../../types";

const TYPE_COLORS: Record<EntityType, string> = {
  person: "#4f86c6",
  company: "#f0a500",
  domain: "#2ecc71",
  email: "#9b59b6",
  phone: "#e74c3c",
  address: "#1abc9c",
  ip: "#e67e22",
  username: "#3498db",
  document: "#95a5a6",
  vessel: "#16a085",
  aircraft: "#8e44ad",
};

const TYPE_ORDER: EntityType[] = [
  "person", "company", "domain", "email", "username",
  "ip", "address", "phone", "document", "aircraft", "vessel",
];

interface Props {
  entities: Entity[];
  selectedEntity: Entity | null;
  onSelect: (entity: Entity) => void;
}

export function EntityList({ entities, selectedEntity, onSelect }: Props) {
  const grouped = TYPE_ORDER.reduce<Record<string, Entity[]>>((acc, type) => {
    const group = entities.filter((e) => e.type === type && e.source_module !== "user");
    if (group.length > 0) acc[type] = group;
    return acc;
  }, {});

  const isEmpty = entities.filter((e) => e.source_module !== "user").length === 0;

  return (
    <aside className="w-64 border-l border-gray-800 bg-gray-900 flex flex-col overflow-hidden flex-shrink-0">
      <div className="px-3 py-2 border-b border-gray-800 text-xs text-gray-400 uppercase tracking-wide flex items-center justify-between">
        <span>Entities</span>
        <span className="text-gray-600">{entities.filter((e) => e.source_module !== "user").length}</span>
      </div>

      <div className="flex-1 overflow-y-auto">
        {isEmpty && (
          <p className="text-xs text-gray-600 italic p-3">
            No entities yet — run a module.
          </p>
        )}

        {Object.entries(grouped).map(([type, group]) => (
          <div key={type}>
            <div className="px-3 py-1 flex items-center gap-1.5 sticky top-0 bg-gray-900 border-b border-gray-800/50 z-10">
              <span
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ backgroundColor: TYPE_COLORS[type as EntityType] ?? "#aaa" }}
              />
              <span className="text-[10px] text-gray-500 uppercase tracking-wide">{type}</span>
              <span className="text-[10px] text-gray-700 ml-auto">{group.length}</span>
            </div>

            {group.map((entity) => {
              const isSelected = selectedEntity?.id === entity.id;
              return (
                <div
                  key={entity.id}
                  onClick={() => onSelect(entity)}
                  className={`
                    flex items-start justify-between px-3 py-2 cursor-pointer
                    hover:bg-gray-800 transition-colors gap-2
                    ${isSelected ? "bg-gray-800 border-l-2 border-blue-500" : "border-l-2 border-transparent"}
                  `}
                >
                  <div className="flex flex-col min-w-0 flex-1">
                    <span className="text-xs text-white break-words leading-tight">
                      {entity.label}
                    </span>
                    {entity.source_url && (
                      <a
                        href={entity.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className="text-[10px] text-blue-500 hover:text-blue-400 truncate mt-0.5"
                      >
                        ↗ source
                      </a>
                    )}
                  </div>
                  <span className="text-[9px] text-gray-600 bg-gray-800 px-1 py-0.5 rounded flex-shrink-0 mt-0.5">
                    {entity.source_module.replace(/_/g, " ")}
                  </span>
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </aside>
  );
}
