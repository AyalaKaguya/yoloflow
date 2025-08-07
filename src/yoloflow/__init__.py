"""
YOLOFlow - YOLO工作流平台

A comprehensive workflow platform for YOLO-based computer vision projects.
Provides project management, dataset handling, model training, and export capabilities.
"""

from .__version__ import __version__
from .cli import main
from .ui import SplashScreen, show_splash_screen
from .model import Project, ProjectConfig, TaskType
from .service import ProjectManager

__all__ = [
    '__version__',
    'main',
    'SplashScreen', 
    'show_splash_screen',
    'Project',
    'ProjectConfig',
    'TaskType',
    'ProjectManager',
]
