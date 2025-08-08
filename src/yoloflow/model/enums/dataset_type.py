from enum import Enum


class DatasetType(Enum):
    """Dataset types based on task types."""
    CLASSIFICATION = "classification"
    DETECTION = "detection"
    SEGMENTATION = "segmentation"
    INSTANCE_SEGMENTATION = "instance_segmentation"
    KEYPOINT = "keypoint"
    ORIENTED_DETECTION = "oriented_detection"