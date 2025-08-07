"""
Model module for YOLOFlow.
Contains data models and configuration classes.
"""

from .project import Project
from .project_config import ProjectConfig, TaskType

__all__ = ['Project', 'ProjectConfig', 'TaskType']
