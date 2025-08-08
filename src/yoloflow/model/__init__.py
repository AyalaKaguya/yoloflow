"""
Model module for YOLOFlow.
Contains data models and configuration classes.
"""

from .project import Project
from .project_config import ProjectConfig
from .task_type import TaskType
from .dataset_manager import DatasetManager
from .dataset_type import DatasetType
from .dataset_info import DatasetInfo
from .model_selector import ModelSelector, get_model_selector, register_custom_model
from .model_info import ModelInfo

__all__ = [
    'Project', 'ProjectConfig', 'TaskType', 
    'DatasetManager', 'DatasetInfo', 'DatasetType',
    'ModelSelector', 'ModelInfo', 'get_model_selector', 'register_custom_model'
]
