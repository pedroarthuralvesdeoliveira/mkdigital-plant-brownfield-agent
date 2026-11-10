from __future__ import annotations

from typing import Dict, List

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from brownfield.application.use_cases import ReconstructPlantUseCase
from brownfield.domain.models import EdgeRelation, NodeCategory, ReconstructionState
from brownfield.infrastructure.repositories import InMemoryPlantTopologyRepository

app = FastAPI(
    title="MKdigital — Plant Brownfield Reconstruction Agent API",
    description="Clean-architecture GraphDB reconstruction service for P&ID and E&I industrial engineering.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class NodeModel(BaseModel):
    tag: str
    category: NodeCategory
    name: str
    source_document: str
    specs: Dict[str, str]
    confidence: float


class EdgeModel(BaseModel):
    source_tag: str
    target_tag: str
    relation: EdgeRelation
    line_spec: str


class AnomalyModel(BaseModel):
    rule_id: str
    severity: str
    affected_tags: List[str]
    description: str


class ReconstructionResponse(BaseModel):
    unit_name: str
    state: ReconstructionState
    state_history: List[ReconstructionState]
    nodes: List[NodeModel]
    edges: List[EdgeModel]
    anomalies: List[AnomalyModel]
    cypher_query: str


def get_use_case() -> ReconstructPlantUseCase:
    return ReconstructPlantUseCase(repository=InMemoryPlantTopologyRepository())


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "mkdigital-plant-brownfield-agent"}


@app.get("/api/v1/brownfield/graph", response_model=ReconstructionResponse)
def reconstruct_graph(
    use_case: ReconstructPlantUseCase = Depends(get_use_case),
) -> ReconstructionResponse:
    result = use_case.execute()
    return ReconstructionResponse(
        unit_name=result.unit_name,
        state=result.state,
        state_history=list(result.state_history),
        nodes=[
            NodeModel(
                tag=n.tag,
                category=n.category,
                name=n.name,
                source_document=n.source_document,
                specs=n.specs,
                confidence=n.confidence,
            )
            for n in result.nodes
        ],
        edges=[
            EdgeModel(
                source_tag=e.source_tag,
                target_tag=e.target_tag,
                relation=e.relation,
                line_spec=e.line_spec,
            )
            for e in result.edges
        ],
        anomalies=[
            AnomalyModel(
                rule_id=a.rule_id,
                severity=a.severity,
                affected_tags=list(a.affected_tags),
                description=a.description,
            )
            for a in result.anomalies
        ],
        cypher_query=result.cypher_query,
    )
