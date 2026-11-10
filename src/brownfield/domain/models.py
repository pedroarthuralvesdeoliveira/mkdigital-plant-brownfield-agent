from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Dict, FrozenSet, List, Set, Tuple


class NodeCategory(StrEnum):
    EQUIPMENT = "EQUIPMENT"
    INSTRUMENT = "INSTRUMENT"
    VALVE = "VALVE"
    ELECTRICAL = "ELECTRICAL"
    CONTROLLER = "CONTROLLER"


class EdgeRelation(StrEnum):
    PROCESS_LINE = "PROCESS_LINE"
    PROCESS_TAP = "PROCESS_TAP"
    SIGNAL_4_20MA = "SIGNAL_4_20MA"
    POWER_FEED = "POWER_FEED"
    CONTROL_LOOP = "CONTROL_LOOP"


class ReconstructionState(StrEnum):
    RAW_DOCUMENTS_LOADED = "RAW_DOCUMENTS_LOADED"
    ENTITIES_EXTRACTED = "ENTITIES_EXTRACTED"
    TOPOLOGY_LINKED = "TOPOLOGY_LINKED"
    ANOMALIES_EVALUATED = "ANOMALIES_EVALUATED"
    CYPHER_EXPORTED = "CYPHER_EXPORTED"


ALLOWED_RECONSTRUCTION_TRANSITIONS: Dict[ReconstructionState, FrozenSet[ReconstructionState]] = {
    ReconstructionState.RAW_DOCUMENTS_LOADED: frozenset({ReconstructionState.ENTITIES_EXTRACTED}),
    ReconstructionState.ENTITIES_EXTRACTED: frozenset({ReconstructionState.TOPOLOGY_LINKED}),
    ReconstructionState.TOPOLOGY_LINKED: frozenset({ReconstructionState.ANOMALIES_EVALUATED}),
    ReconstructionState.ANOMALIES_EVALUATED: frozenset({ReconstructionState.CYPHER_EXPORTED}),
    ReconstructionState.CYPHER_EXPORTED: frozenset(),
}


def advance_reconstruction_state(
    current: ReconstructionState, target: ReconstructionState
) -> ReconstructionState:
    if target not in ALLOWED_RECONSTRUCTION_TRANSITIONS.get(current, frozenset()):
        raise ValueError(f"Illegal reconstruction state transition: {current} -> {target}")
    return target


@dataclass(frozen=True)
class PlantEntityNode:
    tag: str
    category: NodeCategory
    name: str
    source_document: str
    specs: Dict[str, str]
    confidence: float


@dataclass(frozen=True)
class PlantEdge:
    source_tag: str
    target_tag: str
    relation: EdgeRelation
    line_spec: str


@dataclass(frozen=True)
class EngineeringAnomaly:
    rule_id: str
    severity: str
    affected_tags: Tuple[str, ...]
    description: str


@dataclass
class PlantGraph:
    unit_name: str
    _nodes: Dict[str, PlantEntityNode] = field(default_factory=dict)
    _outgoing: Dict[str, List[PlantEdge]] = field(default_factory=dict)
    _incoming: Dict[str, List[PlantEdge]] = field(default_factory=dict)

    def add_node(self, node: PlantEntityNode) -> None:
        self._nodes[node.tag] = node
        self._outgoing.setdefault(node.tag, [])
        self._incoming.setdefault(node.tag, [])

    def add_edge(self, edge: PlantEdge) -> None:
        if edge.source_tag not in self._nodes or edge.target_tag not in self._nodes:
            raise KeyError(f"Cannot link unknown tags: {edge.source_tag} -> {edge.target_tag}")
        self._outgoing[edge.source_tag].append(edge)
        self._incoming[edge.target_tag].append(edge)

    def get_node(self, tag: str) -> PlantEntityNode | None:
        return self._nodes.get(tag)

    def nodes(self) -> Tuple[PlantEntityNode, ...]:
        return tuple(self._nodes.values())

    def edges(self) -> Tuple[PlantEdge, ...]:
        return tuple(edge for group in self._outgoing.values() for edge in group)

    def incident_edges(self, tag: str) -> Tuple[PlantEdge, ...]:
        return tuple(self._outgoing.get(tag, []) + self._incoming.get(tag, []))

    def has_undirected_path(self, start_tag: str, goal_tag: str) -> bool:
        if start_tag not in self._nodes or goal_tag not in self._nodes:
            return False
        visited: Set[str] = {start_tag}
        queue: deque[str] = deque([start_tag])
        while queue:
            current = queue.popleft()
            if current == goal_tag:
                return True
            neighbors = [e.target_tag for e in self._outgoing.get(current, [])] + [
                e.source_tag for e in self._incoming.get(current, [])
            ]
            for nxt in neighbors:
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)
        return False
