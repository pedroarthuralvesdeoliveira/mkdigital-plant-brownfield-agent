from __future__ import annotations

from typing import List, Protocol, Tuple

from brownfield.domain.models import (
    EdgeRelation,
    EngineeringAnomaly,
    NodeCategory,
    PlantGraph,
)


class BrownfieldAnomalyRule(Protocol):
    def evaluate(self, graph: PlantGraph) -> List[EngineeringAnomaly]: ...


class UnwiredInstrumentRule:
    def __init__(self, controller_tag: str = "PLC-RIO-02") -> None:
        self._controller_tag = controller_tag

    def evaluate(self, graph: PlantGraph) -> List[EngineeringAnomaly]:
        anomalies: List[EngineeringAnomaly] = []
        for node in graph.nodes():
            if node.category != NodeCategory.INSTRUMENT:
                continue
            has_signal_link = any(
                (edge.source_tag == self._controller_tag or edge.target_tag == self._controller_tag)
                and edge.relation in {EdgeRelation.SIGNAL_4_20MA, EdgeRelation.CONTROL_LOOP}
                for edge in graph.incident_edges(node.tag)
            )
            if not has_signal_link:
                anomalies.append(
                    EngineeringAnomaly(
                        rule_id="ENG-RULE-01-UNWIRED-INSTRUMENT",
                        severity="HIGH",
                        affected_tags=(node.tag, self._controller_tag),
                        description=(
                            f"Instrument {node.tag} ({node.name}) extracted from {node.source_document} "
                            f"has no signal termination on controller {self._controller_tag}."
                        ),
                    )
                )
        return anomalies


class MetallurgyTransitionRule:
    def evaluate(self, graph: PlantGraph) -> List[EngineeringAnomaly]:
        anomalies: List[EngineeringAnomaly] = []
        for node in graph.nodes():
            if node.category != NodeCategory.EQUIPMENT:
                continue
            incident = graph.incident_edges(node.tag)
            has_stainless = any("SS316" in e.line_spec for e in incident)
            has_carbon_steel = any("-CS" in e.line_spec for e in incident)
            if has_stainless and has_carbon_steel:
                anomalies.append(
                    EngineeringAnomaly(
                        rule_id="ENG-RULE-04-METALLURGY-TRANSITION",
                        severity="MEDIUM",
                        affected_tags=(node.tag,),
                        description=(
                            f"Equipment {node.tag} bridges SS316L stainless steel and carbon steel (CS) "
                            "piping; verify galvanic isolation and corrosion allowance."
                        ),
                    )
                )
        return anomalies


DEFAULT_RULES: Tuple[BrownfieldAnomalyRule, ...] = (
    UnwiredInstrumentRule(),
    MetallurgyTransitionRule(),
)


def export_cypher(graph: PlantGraph) -> str:
    statements: List[str] = ["// Neo4j / Memgraph Cypher Reconstruction Export"]
    for node in graph.nodes():
        statements.append(
            f"MERGE (:{node.category.value} "
            f"{{tag: '{node.tag}', name: '{node.name}', source: '{node.source_document}', confidence: {node.confidence}}});"
        )
    for edge in graph.edges():
        statements.append(
            f"MATCH (a {{tag: '{edge.source_tag}'}}), (b {{tag: '{edge.target_tag}'}}) "
            f"MERGE (a)-[:{edge.relation.value} {{spec: '{edge.line_spec}'}}]->(b);"
        )
    return "\n".join(statements)
