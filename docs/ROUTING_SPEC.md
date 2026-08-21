# ROUTING SPECIFICATION: CACTUS HYBRID CONTRACT

## 1. Typed Contract Schema
```python
class RoutingDecision(BaseModel):
    route: Literal["LOCAL_EDGE", "CLOUD_FRONTIER"]
    intent: str
    confidence: float
    confidence_source: ConfidenceSource
    agent: str | None
    tool: str | None
    reason: str
    escalation_reason: str | None
    metadata: Dict[str, Any]
```

## 2. Thresholds & Escalation Policies
- `READ_THRESHOLD`: 0.80
- `WRITE_THRESHOLD`: 0.90
- `MUTATION_THRESHOLD`: 0.95
- `HIGH_IMPACT_REQUIRES_HUMAN`: True
