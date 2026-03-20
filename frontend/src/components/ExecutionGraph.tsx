import ReactFlow, { Background, Controls, type Node, type Edge } from "reactflow";
import "reactflow/dist/style.css";

export default function ExecutionGraph({
  graph,
}: {
  graph: {
    nodes: Array<{
      id: string;
      label: string;
      latency_ms?: number;
      estimated_cost_usd?: number;
    }>;
    edges: Array<{
      from_node: string;
      to_node: string;
      edge_type: string;
      reason?: string | null;
    }>;
  };
}) {
  const nodes: Node[] = graph.nodes.map((node, index) => ({
    id: node.id,
    position: { x: 80 + index * 280, y: 140 },
    data: {
      label: `${node.label}\n${node.latency_ms ?? 0} ms\n$${node.estimated_cost_usd ?? 0}`,
    },
    style: {
      background: "#1f2937",
      color: "#fff",
      border: "1px solid #374151",
      borderRadius: 18,
      padding: 12,
      width: 200,
      whiteSpace: "pre-line",
      fontWeight: 600,
      boxShadow: "0 10px 24px rgba(0,0,0,0.25)",
    },
  }));

  const edges: Edge[] = graph.edges.map((edge, idx) => ({
    id: `${edge.from_node}-${edge.to_node}-${idx}`,
    source: edge.from_node,
    target: edge.to_node,
    label: edge.reason || edge.edge_type,
    animated: true,
  }));

  return (
    <div className="card" style={{ padding: 12, height: 460 }}>
      <h3 className="card-title" style={{ padding: "6px 6px 0 6px" }}>
        Execution Graph
      </h3>
      <div style={{ height: 390 }}>
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <Background />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
}