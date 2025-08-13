"""
Plan information management.
"""

from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime
from ..enums import PlanStatus


@dataclass
class PlanInfo:
    """
    Basic information about a training plan.
    
    Stores essential metadata about plans for quick access.
    """
    
    plan_id: str  # Unique plan identifier (UUID)
    name: str  # User-defined plan name
    file_path: str  # Relative path to plan file (e.g., "plan/uuid.toml")
    created_at: str  # ISO format timestamp
    status: PlanStatus  # Plan status (PlanStatus enum)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "plan_id": self.plan_id,
            "name": self.name,
            "file_path": self.file_path,
            "created_at": self.created_at,
            "status": self.status.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlanInfo":
        """Create from dictionary."""
        return cls(
            plan_id=data["plan_id"],
            name=data["name"],
            file_path=data["file_path"],
            created_at=data.get("created_at", datetime.now().isoformat()),
            status=data.get("status", PlanStatus.Pending)
        )
    
    @classmethod
    def create_new(cls, plan_id: str, name: str, file_path: str) -> "PlanInfo":
        """Create info for a new plan."""
        return cls(
            plan_id=plan_id,
            name=name,
            file_path=file_path,
            created_at=datetime.now().isoformat(),
            status=PlanStatus.Pending
        )

    def update_status(self, new_status: PlanStatus):
        """Update plan status."""
        self.status = new_status
    
    def __str__(self) -> str:
        return f"{self.name} ({self.status})"
    
    def __repr__(self) -> str:
        return f"PlanInfo(name='{self.name}', status='{self.status}', id='{self.plan_id}')"
