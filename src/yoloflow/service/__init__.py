"""
Service module for YOLOFlow.
Contains business logic, data management, and core services.
"""

from .project_manager import ProjectManager
from .backend_manager import BackendManager

__all__ = ['ProjectManager', 'BackendManager']
