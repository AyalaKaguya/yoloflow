"""
针对不同的检测后端（如ultralytics、detectron2、mmdetection等）进行的平台抽象模块
"""

from .backend_base import BackendBase

__all__ = [
    "BackendBase"
]