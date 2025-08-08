from enum import Enum

class TaskType(Enum):
    """Supported task types for YOLO projects."""
    CLASSIFICATION = "classification"
    DETECTION = "detection"
    SEGMENTATION = "segmentation"
    INSTANCE_SEGMENTATION = "instance_segmentation"
    KEYPOINT = "keypoint"
    ORIENTED_DETECTION = "oriented_detection"