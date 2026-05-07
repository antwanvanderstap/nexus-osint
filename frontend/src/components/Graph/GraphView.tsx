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
        label: e.label.length > 16 ? e.label.slice(0, 14) + "…" : e.label,
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
      layout={{
        name: "fcose",
        nodeRepulsion: 6000,
        idealEdgeLength: 120,
        animate: true,
      } as cytoscape.LayoutOptions}
      stylesheet={[
        {
          selector: "node",
          style: {
            "background-color": "data(color)",
            label: "data(label)",
            color: "#ddd",
            "font-size": 9,
            "font-weight": "normal",
            "text-valign": "bottom",
            "text-halign": "center",
            "text-margin-y": 5,
            "text-background-color": "#111",
            "text-background-opacity": 0.7,
            "text-background-padding": "2px",
            width: 20,
            height: 20,
          },
        },
        {
          selector: "edge",
          style: {
            width: 1,
            "line-color": "#444",
            "target-arrow-color": "#444",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            label: "",
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
