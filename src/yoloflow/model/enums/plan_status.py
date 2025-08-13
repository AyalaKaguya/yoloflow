from enum import Enum


class PlanStatus(Enum):
    """Docstring for PlanStatus."""
    Pending = "pending"
    Running = "running"
    Completed = "completed"
    Failed = "failed"
