"""
Model selection and management for YOLOFlow projects.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Any, TYPE_CHECKING
from ..enums import TaskType
from .model_info import ModelInfo

if TYPE_CHECKING:
    from ...service.backend_manager import BackendManager


class ModelSelector:
    """
    Model selection utility for YOLOFlow projects.
    
    Manages a registry of available models from backend manager and provides filtering
    capabilities based on task type.
    """
    
    def __init__(self, backend_manager: Optional['BackendManager'] = None):
        """Initialize model selector with backend manager.
        
        Args:
            backend_manager: Backend manager instance to get models from
        """
        self._backend_manager = backend_manager
        self._models: List[ModelInfo] = []
        self._register_default_models()
        if self._backend_manager:
            self._sync_from_backend_manager()
    
    def _register_default_models(self):
        """Register default YOLO models from YOLOv11 series."""
        # YOLOv11 Nano models
        self.register_model(ModelInfo(
            name="YOLO 11 Nano - 检测",
            filename="yolo11n.pt",
            parameters="2.6M",
            supported_tasks=frozenset({TaskType.DETECTION}),
            description="YOLOv11 最轻量级模型，适合移动设备和边缘计算"
        ))
        
        self.register_model(ModelInfo(
            name="YOLO 11 Nano - 分类",
            filename="yolo11n-cls.pt",
            parameters="2.6M",
            supported_tasks=frozenset({TaskType.CLASSIFICATION}),
            description="YOLOv11 Nano 分类模型，适合图像分类任务"
        ))
        
        self.register_model(ModelInfo(
            name="YOLO 11 Nano - 分割",
            filename="yolo11n-seg.pt",
            parameters="2.7M",
            supported_tasks=frozenset({TaskType.SEGMENTATION, TaskType.INSTANCE_SEGMENTATION}),
            description="YOLOv11 Nano 分割模型，支持语义分割和实例分割"
        ))
        
        self.register_model(ModelInfo(
            name="YOLO 11 Nano - 姿态估计",
            filename="yolo11n-pose.pt",
            parameters="2.9M",
            supported_tasks=frozenset({TaskType.KEYPOINT}),
            description="YOLOv11 Nano 姿态估计模型，用于关键点检测"
        ))
        
        self.register_model(ModelInfo(
            name="YOLO 11 Nano - 有向检测",
            filename="yolo11n-obb.pt",
            parameters="2.8M",
            supported_tasks=frozenset({TaskType.ORIENTED_DETECTION}),
            description="YOLOv11 Nano 有向边界框检测模型"
        ))
        
        # YOLOv11 Small models
        self.register_model(ModelInfo(
            name="YOLO 11 Small - 检测",
            filename="yolo11s.pt",
            parameters="9.4M",
            supported_tasks=frozenset({TaskType.DETECTION}),
            description="YOLOv11 小型模型，平衡速度和精度"
        ))
        
        self.register_model(ModelInfo(
            name="YOLO 11 Small - 分类",
            filename="yolo11s-cls.pt",
            parameters="9.4M",
            supported_tasks=frozenset({TaskType.CLASSIFICATION}),
            description="YOLOv11 Small 分类模型"
        ))
        
        self.register_model(ModelInfo(
            name="YOLO 11 Small - 分割",
            filename="yolo11s-seg.pt",
            parameters="9.5M",
            supported_tasks=frozenset({TaskType.SEGMENTATION, TaskType.INSTANCE_SEGMENTATION}),
            description="YOLOv11 Small 分割模型"
        ))
        
        self.register_model(ModelInfo(
            name="YOLO 11 Small - 姿态估计",
            filename="yolo11s-pose.pt",
            parameters="9.7M",
            supported_tasks=frozenset({TaskType.KEYPOINT}),
            description="YOLOv11 Small 姿态估计模型"
        ))
        
        self.register_model(ModelInfo(
            name="YOLO 11 Small - 有向检测",
            filename="yolo11s-obb.pt",
            parameters="9.6M",
            supported_tasks=frozenset({TaskType.ORIENTED_DETECTION}),
            description="YOLOv11 Small 有向边界框检测模型"
        ))
        
        # YOLOv11 Medium models
        self.register_model(ModelInfo(
            name="YOLO 11 Medium - 检测",
            filename="yolo11m.pt",
            parameters="20.1M",
            supported_tasks=frozenset({TaskType.DETECTION}),
            description="YOLOv11 中型模型，更高精度"
        ))
        
        self.register_model(ModelInfo(
            name="YOLO 11 Medium - 分类",
            filename="yolo11m-cls.pt",
            parameters="20.1M",
            supported_tasks=frozenset({TaskType.CLASSIFICATION}),
            description="YOLOv11 Medium 分类模型"
        ))
        
        self.register_model(ModelInfo(
            name="YOLO 11 Medium - 分割",
            filename="yolo11m-seg.pt",
            parameters="22.5M",
            supported_tasks=frozenset({TaskType.SEGMENTATION, TaskType.INSTANCE_SEGMENTATION}),
            description="YOLOv11 Medium 分割模型"
        ))
        
        self.register_model(ModelInfo(
            name="YOLO 11 Medium - 姿态估计",
            filename="yolo11m-pose.pt",
            parameters="20.9M",
            supported_tasks=frozenset({TaskType.KEYPOINT}),
            description="YOLOv11 Medium 姿态估计模型"
        ))
        
        self.register_model(ModelInfo(
            name="YOLO 11 Medium - 有向检测",
            filename="yolo11m-obb.pt",
            parameters="20.9M",
            supported_tasks=frozenset({TaskType.ORIENTED_DETECTION}),
            description="YOLOv11 Medium 有向边界框检测模型"
        ))
        
        # YOLOv11 Large models
        self.register_model(ModelInfo(
            name="YOLO 11 Large - 检测",
            filename="yolo11l.pt",
            parameters="25.3M",
            supported_tasks=frozenset({TaskType.DETECTION}),
            description="YOLOv11 大型模型，高精度应用"
        ))
        
        self.register_model(ModelInfo(
            name="YOLO 11 Large - 分类",
            filename="yolo11l-cls.pt",
            parameters="25.3M",
            supported_tasks=frozenset({TaskType.CLASSIFICATION}),
            description="YOLOv11 Large 分类模型"
        ))
        
        self.register_model(ModelInfo(
            name="YOLO 11 Large - 分割",
            filename="yolo11l-seg.pt",
            parameters="27.6M",
            supported_tasks=frozenset({TaskType.SEGMENTATION, TaskType.INSTANCE_SEGMENTATION}),
            description="YOLOv11 Large 分割模型"
        ))
        
        self.register_model(ModelInfo(
            name="YOLO 11 Large - 姿态估计",
            filename="yolo11l-pose.pt",
            parameters="26.2M",
            supported_tasks=frozenset({TaskType.KEYPOINT}),
            description="YOLOv11 Large 姿态估计模型"
        ))
        
        self.register_model(ModelInfo(
            name="YOLO 11 Large - 有向检测",
            filename="yolo11l-obb.pt",
            parameters="26.2M",
            supported_tasks=frozenset({TaskType.ORIENTED_DETECTION}),
            description="YOLOv11 Large 有向边界框检测模型"
        ))
        
        # YOLOv11 Extra Large models
        self.register_model(ModelInfo(
            name="YOLO 11 Extra Large - 检测",
            filename="yolo11x.pt",
            parameters="56.9M",
            supported_tasks=frozenset({TaskType.DETECTION}),
            description="YOLOv11 超大型模型，最高精度"
        ))
        
        self.register_model(ModelInfo(
            name="YOLO 11 Extra Large - 分类",
            filename="yolo11x-cls.pt",
            parameters="56.9M",
            supported_tasks=frozenset({TaskType.CLASSIFICATION}),
            description="YOLOv11 Extra Large 分类模型"
        ))
        
        self.register_model(ModelInfo(
            name="YOLO 11 Extra Large - 分割",
            filename="yolo11x-seg.pt",
            parameters="58.8M",
            supported_tasks=frozenset({TaskType.SEGMENTATION, TaskType.INSTANCE_SEGMENTATION}),
            description="YOLOv11 Extra Large 分割模型"
        ))
        
        self.register_model(ModelInfo(
            name="YOLO 11 Extra Large - 姿态估计",
            filename="yolo11x-pose.pt",
            parameters="58.2M",
            supported_tasks=frozenset({TaskType.KEYPOINT}),
            description="YOLOv11 Extra Large 姿态估计模型"
        ))
        
        self.register_model(ModelInfo(
            name="YOLO 11 Extra Large - 有向检测",
            filename="yolo11x-obb.pt",
            parameters="58.2M",
            supported_tasks=frozenset({TaskType.ORIENTED_DETECTION}),
            description="YOLOv11 Extra Large 有向边界框检测模型"
        ))
    
    def _sync_from_backend_manager(self):
        """Sync models from backend manager."""
        if not self._backend_manager:
            return
        
        # Get all models from backend manager
        backend_models = self._backend_manager.get_supported_models()
        for model in backend_models:
            # Backend models are added directly (they have from_backend field)
            # They may have the same filename as default models but provide backend-specific functionality
            self._models.append(model)
    
    def set_backend_manager(self, backend_manager: 'BackendManager'):
        """Set backend manager and sync models.
        
        Args:
            backend_manager: Backend manager instance
        """
        self._backend_manager = backend_manager
        self._sync_from_backend_manager()
    
    def refresh_models(self):
        """Refresh models from backend manager."""
        if self._backend_manager:
            # Remove existing backend models first
            self._models = [m for m in self._models if not m.from_backend]
            # Add current backend models
            self._sync_from_backend_manager()
    
    def register_model(self, model_info: ModelInfo):
        """
        Register a new model in the selector.
        
        Args:
            model_info: Model information to register
        """
        # Check for duplicate filenames
        for existing_model in self._models:
            if existing_model.filename == model_info.filename:
                # Update existing model instead of adding duplicate
                self._models.remove(existing_model)
                break
        
        self._models.append(model_info)
    
    def get_models_for_task(self, task_type: TaskType) -> List[ModelInfo]:
        """
        Get all models that support the given task type.
        
        Args:
            task_type: The task type to filter by
            
        Returns:
            List of models supporting the task type
        """
        return [model for model in self._models if model.supports_task(task_type)]
    
    def get_model_by_filename(self, filename: str) -> Optional[ModelInfo]:
        """
        Get model by filename.
        
        Args:
            filename: Model filename to search for
            
        Returns:
            Model info if found, None otherwise
        """
        for model in self._models:
            if model.filename == filename:
                return model
        return None
    
    def get_model_by_name(self, name: str) -> Optional[ModelInfo]:
        """
        Get model by display name.
        
        Args:
            name: Model display name to search for
            
        Returns:
            Model info if found, None otherwise
        """
        for model in self._models:
            if model.name == name:
                return model
        return None
    
    def get_all_models(self) -> List[ModelInfo]:
        """
        Get all registered models.
        
        Returns:
            List of all models
        """
        return self._models.copy()
    
    def get_supported_tasks(self) -> Set[TaskType]:
        """
        Get all task types supported by any registered model.
        
        Returns:
            Set of supported task types
        """
        tasks = set()
        for model in self._models:
            tasks.update(model.supported_tasks)
        return tasks
    
    def get_recommended_model(self, task_type: TaskType, prefer_small: bool = True) -> Optional[ModelInfo]:
        """
        Get recommended model for a task type.
        
        Args:
            task_type: Task type to get recommendation for
            prefer_small: Whether to prefer smaller models (default True)
            
        Returns:
            Recommended model or None if no models support the task
        """
        models = self.get_models_for_task(task_type)
        if not models:
            return None
        
        if prefer_small:
            # Find the nano model first, then small
            for model in models:
                if "nano" in model.name.lower():
                    return model
            for model in models:
                if "small" in model.name.lower():
                    return model
        else:
            # Find the largest model
            for model in reversed(models):
                if "extra large" in model.name.lower():
                    return model
            for model in reversed(models):
                if "large" in model.name.lower():
                    return model
        
        # Return first available model as fallback
        return models[0]
    
    def search_models(self, query: str) -> List[ModelInfo]:
        """
        Search models by name or description.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching models
        """
        query = query.lower()
        matches = []
        
        for model in self._models:
            if (query in model.name.lower() or 
                query in model.description.lower() or
                query in model.filename.lower()):
                matches.append(model)
        
        return matches
    
    def get_model_count(self) -> int:
        """Get total number of registered models."""
        return len(self._models)
    
    def get_model_count_by_task(self, task_type: TaskType) -> int:
        """Get number of models supporting a specific task."""
        return len(self.get_models_for_task(task_type))
    
    def __str__(self) -> str:
        return f"ModelSelector({self.get_model_count()} models registered)"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    