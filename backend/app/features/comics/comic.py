from dataclasses import dataclass
from datetime import datetime

@dataclass
class Comic:
    """Comic book model"""
    id: int
    serie: str
    number: str
    title: str
    created_by: str  # FK to User.uuid
    created_at: datetime
    updated_at: datetime