const PLANT_NODES = [
  {
    tag: "TK-101",
    category: "EQUIPMENT",
    name: "Feed Buffer Tank",
    source_document: "PID-CH-ZUR-101-Rev3.pdf",
    specs: { Volume: "25 m3", Material: "SS316L", "Design Pressure": "6 bar" },
    confidence: 0.99,
    x: 110,
    y: 210
  },
  {
    tag: "LIT-101",
    category: "INSTRUMENT",
    name: "Radar Level Transmitter",
    source_document: "PID-CH-ZUR-101-Rev3.pdf",
    specs: { Signal: "4-20mA HART", Range: "0–5000 mm", Interlock: "LAHH/LALL-101" },
    confidence: 0.97,
    x: 110,
    y: 75
  },
  {
    tag: "P-101A",
    category: "EQUIPMENT",
    name: "Main Transfer Centrifugal Pump",
    source_document: "PID-CH-ZUR-101-Rev3.pdf + Field-Photo-04.jpg",
    specs: { Power: "45 kW", Flow: "120 m3/h", Head: "85 m" },
    confidence: 0.98,
    x: 310,
    y: 210
  },
  {
    tag: "MCC-01-B04",
    category: "ELECTRICAL",
    name: "MCC Feeder 400V (VFD)",
    source_document: "EI-SLD-204-Rev2.pdf",
    specs: { Voltage: "400V AC 3~", Breaker: "100A + VFD", Cable: "3x35mm2 Cu" },
    confidence: 0.96,
    x: 310,
    y: 355
  },
  {
    tag: "PT-103",
    category: "INSTRUMENT",
    name: "Discharge Pressure Transmitter (Unwired)",
    source_document: "Field-Nameplate-Photo-19.jpg",
    specs: { Signal: "4-20mA", Range: "0–16 bar", Status: "Missing termination in EI-WIRING-310" },
    confidence: 0.89,
    anomaly: true,
    x: 310,
    y: 75
  },
  {
    tag: "FIT-102",
    category: "INSTRUMENT",
    name: "Coriolis Mass Flow Transmitter",
    source_document: "PID-CH-ZUR-101-Rev3.pdf",
    specs: { Signal: "4-20mA HART", Line: '4"-P-1012-CS', Accuracy: "±0.15%" },
    confidence: 0.95,
    x: 500,
    y: 210
  },
  {
    tag: "PLC-RIO-02",
    category: "ELECTRICAL",
    name: "Safety PLC Remote I/O Cabinet 02",
    source_document: "EI-WIRING-310.pdf",
    specs: { Protocol: "Profinet / HART", Channels: "32 AI / 16 DO", Location: "Substation B" },
    confidence: 0.99,
    x: 500,
    y: 75
  },
  {
    tag: "FCV-102",
    category: "VALVE",
    name: "Pneumatic Flow Control Valve",
    source_document: "PID-CH-ZUR-101-Rev3.pdf",
    specs: { Cv: "65", "Fail Action": "Fail-Close (FC)", Actuator: "Diaphragm 3-15 psi" },
    confidence: 0.96,
    x: 660,
    y: 210
  },
  {
    tag: "HE-201",
    category: "EQUIPMENT",
    name: "Shell & Tube Heat Exchanger",
    source_document: "PID-CH-ZUR-101-Rev3.pdf",
    specs: { Area: "82 m2", Duty: "1.4 MW", Medium: "Steam / Process Feed" },
    confidence: 0.98,
    x: 800,
    y: 210
  }
];

const PLANT_EDGES = [
  { source: "TK-101", target: "P-101A", relation: "PROCESS_LINE", spec: '6"-P-1011-SS316' },
  { source: "LIT-101", target: "TK-101", relation: "PROCESS_TAP", spec: "DN50 Nozzle N4" },
  { source: "LIT-101", target: "PLC-RIO-02", relation: "SIGNAL_4_20MA", spec: "AI-CH01" },
  { source: "MCC-01-B04", target: "P-101A", relation: "POWER_FEED", spec: "400V AC 3x35mm2" },
  { source: "PT-103", target: "P-101A", relation: "PROCESS_TAP", spec: '1/2" NPT Discharge' },
  { source: "P-101A", target: "FIT-102", relation: "PROCESS_LINE", spec: '4"-P-1012-CS' },
  { source: "FIT-102", target: "PLC-RIO-02", relation: "SIGNAL_4_20MA", spec: "AI-CH04" },
  { source: "FIT-102", target: "FCV-102", relation: "PROCESS_LINE", spec: '4"-P-1012-CS' },
  { source: "PLC-RIO-02", target: "FCV-102", relation: "CONTROL_LOOP", spec: "AO-CH02 (FIC-102)" },
  { source: "FCV-102", target: "HE-201", relation: "PROCESS_LINE", spec: '4"-P-1013-CS' }
];

const PLANT_ANOMALIES = [
  {
    severity: "HIGH",
    rule_id: "ENG-RULE-01-UNWIRED-INSTRUMENT",
    description:
      "Instrument PT-103 extracted from Field-Nameplate-Photo-19.jpg has no 4-20mA signal termination on controller PLC-RIO-02 in EI-WIRING-310.pdf."
  },
  {
    severity: "MEDIUM",
    rule_id: "ENG-RULE-04-METALLURGY-TRANSITION",
    description:
      'Equipment P-101A bridges SS316L stainless steel suction piping (6"-P-1011-SS316) and carbon steel discharge piping (4"-P-1012-CS); verify galvanic isolation.'
  }
];

let activeFilter = "ALL";
let selectedTag = "PT-103";

function getNodeColor(node) {
  if (node.anomaly) return "#f87171";
  switch (node.category) {
    case "EQUIPMENT":
      return "#70befa";
    case "INSTRUMENT":
      return "#34d399";
    case "VALVE":
      return "#fbbf24";
    case "ELECTRICAL":
      return "#c084fc";
    default:
      return "#9c9c9c";
  }
}

function renderGraph() {
  const svg = document.getElementById("plant-svg");
  const nodeMap = Object.fromEntries(PLANT_NODES.map((n) => [n.tag, n]));

  let html = `
    <defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="26" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#525252" />
      </marker>
    </defs>
  `;

  for (const edge of PLANT_EDGES) {
    const s = nodeMap[edge.source];
    const t = nodeMap[edge.target];
    const isSignal = edge.relation === "SIGNAL_4_20MA" || edge.relation === "CONTROL_LOOP";
    const stroke = edge.relation === "POWER_FEED" ? "#c084fc" : isSignal ? "#34d399" : "#70befa";
    const midX = (s.x + t.x) / 2;
    const midY = (s.y + t.y) / 2 - 8;

    html += `
      <g>
        <line x1="${s.x}" y1="${s.y}" x2="${t.x}" y2="${t.y}"
          stroke="${stroke}" stroke-opacity="0.65" stroke-width="2"
          ${isSignal ? 'stroke-dasharray="5,4"' : ""}
          marker-end="url(#arrow)" />
        <text x="${midX}" y="${midY}" fill="#9c9c9c" font-size="9.5" text-anchor="middle">${edge.relation}</text>
      </g>
    `;
  }

  for (const node of PLANT_NODES) {
    const visible = activeFilter === "ALL" || node.category === activeFilter;
    const opacity = visible ? "1" : "0.2";
    const isSelected = node.tag === selectedTag;
    const color = getNodeColor(node);

    html += `
      <g class="graph-node" data-tag="${node.tag}" style="cursor:pointer; opacity:${opacity}">
        ${
          isSelected
            ? `<circle cx="${node.x}" cy="${node.y}" r="31" fill="none" stroke="#ffffff" stroke-width="2" stroke-dasharray="4,3" />`
            : ""
        }
        <circle cx="${node.x}" cy="${node.y}" r="24" fill="#0f0f0f" stroke="${color}" stroke-width="3" />
        <text x="${node.x}" y="${node.y + 4}" fill="#ffffff" font-size="10.5" font-weight="700" text-anchor="middle">${node.tag}</text>
        <text x="${node.x}" y="${node.y + 40}" fill="#9c9c9c" font-size="10.5" text-anchor="middle">${node.name.slice(0, 22)}</text>
      </g>
    `;
  }

  svg.innerHTML = html;
  svg.querySelectorAll(".graph-node").forEach((el) => {
    el.addEventListener("click", () => {
      selectedTag = el.getAttribute("data-tag");
      renderGraph();
      renderInspector(selectedTag);
    });
  });
}

function renderInspector(tag) {
  const node = PLANT_NODES.find((n) => n.tag === tag);
  if (!node) return;

  document.getElementById("bf-node-conf").textContent = `Confidence: ${(node.confidence * 100).toFixed(0)}%`;
  const incident = PLANT_EDGES.filter((e) => e.source === tag || e.target === tag);
  const specsHtml = Object.entries(node.specs)
    .map(([k, v]) => `<div class="kv-row"><span class="kv-label">${k}</span><span class="kv-val">${v}</span></div>`)
    .join("");

  document.getElementById("bf-inspector").innerHTML = `
    <div class="box">
      <div class="kv-row"><span class="kv-label">ISA-5.1 Tag</span><span class="kv-val"><code>${node.tag}</code></span></div>
      <div class="kv-row"><span class="kv-label">Category</span><span class="kv-val">${node.category}</span></div>
      <div class="kv-row"><span class="kv-label">Component</span><span class="kv-val">${node.name}</span></div>
      <div class="kv-row"><span class="kv-label">Source Document</span><span class="kv-val">${node.source_document}</span></div>
      ${specsHtml}
    </div>
    <h4 class="subhead">Incident Graph Edges (${incident.length})</h4>
    <ul class="check-list">
      ${incident.map((e) => `<li><code>${e.source}</code> → <code>${e.target}</code> (${e.relation} · ${e.spec})</li>`).join("")}
    </ul>
  `;
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      document.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      activeFilter = chip.dataset.filter;
      renderGraph();
    });
  });

  document.getElementById("bf-anomalies").innerHTML = PLANT_ANOMALIES.map(
    (a) => `
      <div class="anomaly-item ${a.severity === "MEDIUM" ? "medium" : ""}">
        <strong>[${a.severity}] ${a.rule_id}</strong>
        <p style="color:#9c9c9c">${a.description}</p>
      </div>
    `
  ).join("");

  const cypherLines = [
    "// Neo4j / Memgraph Cypher Reconstruction Export",
    ...PLANT_NODES.map(
      (n) =>
        `MERGE (:${n.category} {tag: '${n.tag}', name: '${n.name}', source: '${n.source_document}', confidence: ${n.confidence}});`
    ),
    ...PLANT_EDGES.map(
      (e) =>
        `MATCH (a {tag: '${e.source}'}), (b {tag: '${e.target}'}) MERGE (a)-[:${e.relation} {spec: '${e.spec}'}]->(b);`
    )
  ];
  document.getElementById("bf-cypher-code").textContent = cypherLines.join("\n");

  document.getElementById("btn-copy-cypher").addEventListener("click", (e) => {
    navigator.clipboard.writeText(document.getElementById("bf-cypher-code").textContent);
    e.target.textContent = "Copied ✓";
    setTimeout(() => (e.target.textContent = "Copy Cypher"), 1800);
  });

  renderGraph();
  renderInspector(selectedTag);
});
