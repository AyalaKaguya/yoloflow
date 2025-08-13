from enum import Enum


class BackendUnavailableReason(Enum):
    """Docstring for BackendUnavailableReason."""

    YoloflowTooNew = "Yoloflow version is too new"
    YoloflowTooOld = "Yoloflow version is too old"

    InternalError = "Internal error occurred"
    
    