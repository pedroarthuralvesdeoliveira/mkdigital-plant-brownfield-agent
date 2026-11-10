import pytest
from fastapi.testclient import TestClient

from brownfield.api.app import app
from brownfield.domain.models import (
    PlantGraph,
    ReconstructionState,
    advance_reconstruction_state,
)
from brownfield.infrastructure.repositories import InMemoryPlantTopologyRepository

client = TestClient(app)


def test_explicit_reconstruction_state_machine_rejects_invalid_jump() -> None:
    with pytest.raises(ValueError):
        advance_reconstruction_state(
            ReconstructionState.RAW_DOCUMENTS_LOADED,
            ReconstructionState.CYPHER_EXPORTED,
        )


def test_adjacency_graph_bfs_connectivity_and_O1_lookup() -> None:
    repo = InMemoryPlantTopologyRepository()
    graph = PlantGraph(unit_name=repo.load_unit_name())
    for node in repo.load_nodes():
        graph.add_node(node)
    for edge in repo.load_edges():
        graph.add_edge(edge)

    assert graph.get_node("P-101A") is not None
    assert graph.has_undirected_path("TK-101", "HE-201") is True


def test_brownfield_endpoint_detects_unwired_instrument_and_exports_cypher() -> None:
    response = client.get("/api/v1/brownfield/graph")
    assert response.status_code == 200
    body = response.json()
    assert body["state"] == "CYPHER_EXPORTED"
    assert body["state_history"] == [
        "RAW_DOCUMENTS_LOADED",
        "ENTITIES_EXTRACTED",
        "TOPOLOGY_LINKED",
        "ANOMALIES_EVALUATED",
        "CYPHER_EXPORTED",
    ]
    rule_ids = {a["rule_id"] for a in body["anomalies"]}
    assert "ENG-RULE-01-UNWIRED-INSTRUMENT" in rule_ids
    assert "ENG-RULE-04-METALLURGY-TRANSITION" in rule_ids
    assert "MERGE" in body["cypher_query"]
