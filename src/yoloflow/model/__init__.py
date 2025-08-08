"""
Model module for YOLOFlow.
Contains data models and configuration classes.
"""

from .project import Project
from .project_config import ProjectConfig
from .dataset_manager import DatasetManager, DatasetType, DatasetInfo
from .model_selector import ModelSelector, ModelInfo, get_model_selector, register_custom_model
from .task_provider import TaskTypeProvider, TaskType, TaskInfo, get_task_provider, register_custom_task

__all__ = [
    'Project', 'ProjectConfig', 'TaskType', 
    'DatasetManager', 'DatasetInfo', 'DatasetType',
    'ModelSelector', 'ModelInfo', 'get_model_selector', 'register_custom_model',
    'TaskTypeProvider', 'TaskInfo', 'get_task_provider', 'register_custom_task'
]
