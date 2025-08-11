from enum import Enum


class DatasetTarget(Enum):
    """Dataset target types for training plans."""
    TRAIN = "train"           # Training set
    VAL = "val"              # Validation set  
    TEST = "test"            # Test set
    MIXED = "mixed"          # Use dataset internal settings
    UNUSED = "unused"        # Unused dataset