from __future__ import annotations

from typing import Sequence

from brownfield.domain.models import (
    EdgeRelation,
    NodeCategory,
    PlantEdge,
    PlantEntityNode,
)


class InMemoryPlantTopologyRepository:
    def load_unit_name(self) -> str:
        return "Zurich Pilot Chemical Feed Unit — Area 100"

    def load_nodes(self) -> Sequence[PlantEntityNode]:
        return (
            PlantEntityNode(
                tag="TK-101",
                category=NodeCategory.EQUIPMENT,
                name="Feed Buffer Tank",
                source_document="PID-CH-ZUR-101-Rev3.pdf",
                specs={"volume": "25 m3", "material": "SS316L", "design_pressure": "6 bar"},
                confidence=0.99,
            ),
            PlantEntityNode(
                tag="LIT-101",
                category=NodeCategory.INSTRUMENT,
                name="Radar Level Transmitter",
                source_document="PID-CH-ZUR-101-Rev3.pdf",
                specs={"signal": "4-20mA HART", "range": "0-5000 mm"},
                confidence=0.97,
            ),
            PlantEntityNode(
                tag="P-101A",
                category=NodeCategory.EQUIPMENT,
                name="Main Transfer Centrifugal Pump",
                source_document="PID-CH-ZUR-101-Rev3.pdf + Field-Photo-04.jpg",
                specs={"power": "45 kW", "flow": "120 m3/h", "head": "85 m"},
                confidence=0.98,
            ),
            PlantEntityNode(
                tag="MCC-01-B04",
                category=NodeCategory.ELECTRICAL,
                name="MCC Feeder 400V (VFD)",
                source_document="EI-SLD-204-Rev2.pdf",
                specs={"voltage": "400V AC", "breaker": "100A VFD"},
                confidence=0.96,
            ),
            PlantEntityNode(
                tag="PT-103",
                category=NodeCategory.INSTRUMENT,
                name="Discharge Pressure Transmitter",
                source_document="Field-Nameplate-Photo-19.jpg",
                specs={"signal": "4-20mA", "range": "0-16 bar"},
                confidence=0.89,
            ),
            PlantEntityNode(
                tag="FIT-102",
                category=NodeCategory.INSTRUMENT,
                name="Coriolis Mass Flow Transmitter",
                source_document="PID-CH-ZUR-101-Rev3.pdf",
                specs={"signal": "4-20mA HART", "line": '4"-P-1012-CS'},
                confidence=0.95,
            ),
            PlantEntityNode(
                tag="PLC-RIO-02",
                category=NodeCategory.CONTROLLER,
                name="Safety PLC Remote I/O Cabinet 02",
                source_document="EI-WIRING-310.pdf",
                specs={"protocol": "Profinet / HART", "channels": "32 AI / 16 DO"},
                confidence=0.99,
            ),
            PlantEntityNode(
                tag="FCV-102",
                category=NodeCategory.VALVE,
                name="Pneumatic Flow Control Valve",
                source_document="PID-CH-ZUR-101-Rev3.pdf",
                specs={"cv": "65", "fail_position": "Fail-Close (FC)"},
                confidence=0.96,
            ),
            PlantEntityNode(
                tag="HE-201",
                category=NodeCategory.EQUIPMENT,
                name="Shell & Tube Heat Exchanger",
                source_document="PID-CH-ZUR-101-Rev3.pdf",
                specs={"area": "82 m2", "duty": "1.4 MW"},
                confidence=0.98,
            ),
        )

    def load_edges(self) -> Sequence[PlantEdge]:
        return (
            PlantEdge("TK-101", "P-101A", EdgeRelation.PROCESS_LINE, '6"-P-1011-SS316'),
            PlantEdge("LIT-101", "TK-101", EdgeRelation.PROCESS_TAP, "DN50 Nozzle N4"),
            PlantEdge("LIT-101", "PLC-RIO-02", EdgeRelation.SIGNAL_4_20MA, "AI-CH01"),
            PlantEdge("MCC-01-B04", "P-101A", EdgeRelation.POWER_FEED, "400V AC 3x35mm2"),
            PlantEdge("PT-103", "P-101A", EdgeRelation.PROCESS_TAP, '1/2" NPT Discharge'),
            PlantEdge("P-101A", "FIT-102", EdgeRelation.PROCESS_LINE, '4"-P-1012-CS'),
            PlantEdge("FIT-102", "PLC-RIO-02", EdgeRelation.SIGNAL_4_20MA, "AI-CH04"),
            PlantEdge("FIT-102", "FCV-102", EdgeRelation.PROCESS_LINE, '4"-P-1012-CS'),
            PlantEdge("PLC-RIO-02", "FCV-102", EdgeRelation.CONTROL_LOOP, "AO-CH02 (FIC-102)"),
            PlantEdge("FCV-102", "HE-201", EdgeRelation.PROCESS_LINE, '4"-P-1013-CS'),
        )
