from pydantic import BaseModel, Field
from typing import List, Optional

class HandoverItem(BaseModel):
    equipment_name: str
    model: str
    serial_no: str
    quantity: int = 1
    manufacturer: Optional[str] = None
    origin_country: Optional[str] = None

class HandoverDocumentSchema(BaseModel):
    handover_date: str
    department: str
    party_a: str
    party_b: str
    contract_no: Optional[str] = None
    items: List[HandoverItem] = []
