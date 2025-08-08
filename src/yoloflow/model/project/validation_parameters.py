"""
Validation parameters for training plans.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ValidationParameters:
    """Validation parameters."""
    confidence_threshold: float = 0.25  # Confidence threshold
    iou_threshold: float = 0.45         # IoU threshold
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "confidence_threshold": self.confidence_threshold,
            "iou_threshold": self.iou_threshold
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationParameters":
        """Create from dictionary."""
        return cls(
            confidence_threshold=data.get("confidence_threshold", 0.25),
            iou_threshold=data.get("iou_threshold", 0.45)
        )
