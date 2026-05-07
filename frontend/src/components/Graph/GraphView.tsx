import CytoscapeComponent from "react-cytoscapejs";
import cytoscape from "cytoscape";
import fcose from "cytoscape-fcose";
import { Entity, Relationship, EntityType } from "../../types";

cytoscape.use(fcose);

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

interface Props {
  entities: Entity[];
  relationships: Relationship[];
  onNodeClick?: (entity: Entity) => void;
}

export function GraphView({ entities, relationships, onNodeClick }: Props) {
  const elements: cytoscape.ElementDefinition[] = [
    ...entities.map((e) => ({
      data: {
        id: e.id,
        label: e.label.length > 24 ? e.label.slice(0, 22) + "…" : e.label,
        type: e.type,
        color: TYPE_COLORS[e.type] ?? "#aaa",
        entity: e,
      },
    })),
    ...relationships.map((r) => ({
      data: {
        source: r.source_id,
        target: r.target_id,
        label: r.type.replace(/_/g, " ").toLowerCase(),
      },
    })),
  ];

  return (
    <CytoscapeComponent
      elements={elements}
      style={{ width: "100%", height: "100%" }}
      layout={{ name: "fcose" } as cytoscape.LayoutOptions}
      stylesheet={[
        {
          selector: "node",
          style: {
            "background-color": "data(color)",
            label: "data(label)",
            color: "#fff",
            "font-size": 11,
            "text-valign": "bottom",
            "text-halign": "center",
            "text-margin-y": 4,
            width: 36,
            height: 36,
          },
        },
        {
          selector: "edge",
          style: {
            width: 1.5,
            "line-color": "#555",
            "target-arrow-color": "#555",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            label: "data(label)",
            "font-size": 9,
            color: "#aaa",
            "text-rotation": "autorotate",
          },
        },
        {
          selector: "node:selected",
          style: { "border-width": 3, "border-color": "#fff" },
        },
      ]}
      cy={(cy: cytoscape.Core) => {
        cy.on("tap", "node", (e: cytoscape.EventObject) => {
          const entity = e.target.data("entity") as Entity;
          if (entity && onNodeClick) onNodeClick(entity);
        });
      }}
    />
  );
}
