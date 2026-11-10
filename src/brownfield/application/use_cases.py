from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol, Sequence, Tuple

from brownfield.domain.models import (
    EngineeringAnomaly,
    PlantEdge,
    PlantEntityNode,
    PlantGraph,
    ReconstructionState,
    advance_reconstruction_state,
)
from brownfield.domain.rules import BrownfieldAnomalyRule, DEFAULT_RULES, export_cypher


class PlantTopologyRepository(Protocol):
    def load_unit_name(self) -> str: ...
    def load_nodes(self) -> Sequence[PlantEntityNode]: ...
    def load_edges(self) -> Sequence[PlantEdge]: ...


@dataclass(frozen=True)
class ReconstructionResult:
    unit_name: str
    state: ReconstructionState
    state_history: Tuple[ReconstructionState, ...]
    nodes: Tuple[PlantEntityNode, ...]
    edges: Tuple[PlantEdge, ...]
    anomalies: Tuple[EngineeringAnomaly, ...]
    cypher_query: str


class ReconstructPlantUseCase:
    def __init__(
        self,
        repository: PlantTopologyRepository,
        rules: Sequence[BrownfieldAnomalyRule] = DEFAULT_RULES,
    ) -> None:
        self._repository = repository
        self._rules = rules

    def execute(self) -> ReconstructionResult:
        state = ReconstructionState.RAW_DOCUMENTS_LOADED
        history: List[ReconstructionState] = [state]

        graph = PlantGraph(unit_name=self._repository.load_unit_name())
        for node in self._repository.load_nodes():
            graph.add_node(node)
        state = advance_reconstruction_state(state, ReconstructionState.ENTITIES_EXTRACTED)
        history.append(state)

        for edge in self._repository.load_edges():
            graph.add_edge(edge)
        state = advance_reconstruction_state(state, ReconstructionState.TOPOLOGY_LINKED)
        history.append(state)

        anomalies: List[EngineeringAnomaly] = []
        for rule in self._rules:
            anomalies.extend(rule.evaluate(graph))
        state = advance_reconstruction_state(state, ReconstructionState.ANOMALIES_EVALUATED)
        history.append(state)

        cypher_query = export_cypher(graph)
        state = advance_reconstruction_state(state, ReconstructionState.CYPHER_EXPORTED)
        history.append(state)

        return ReconstructionResult(
            unit_name=graph.unit_name,
            state=state,
            state_history=tuple(history),
            nodes=graph.nodes(),
            edges=graph.edges(),
            anomalies=tuple(anomalies),
            cypher_query=cypher_query,
        )
