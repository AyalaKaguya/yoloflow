"""
Task type information and provider for project creation wizard.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..enums import TaskType
from .task_info import TaskInfo


class TaskTypeProvider:
    """
    Provider for task type information during project creation.
    
    Manages a registry of task information and provides access
    to task details for the project creation wizard UI.
    
    Note: This class is only used during project creation wizard phase.
    After project creation, the system relies on pure TaskType enum.
    """
    
    def __init__(self):
        """Initialize task type provider with default task information."""
        self._tasks: Dict[TaskType, TaskInfo] = {}
        self._register_default_tasks()
    
    def _register_default_tasks(self):
        """Register default task type information."""
        # Classification task
        self.register_task(TaskInfo(
            task_type=TaskType.CLASSIFICATION,
            name="图像分类",
            description="将整个图像分类到预定义的类别中。适合识别图像中的主要对象或场景类型，如动物分类、场景识别、产品分类等。",
            example_image=None  # Could be set to a resource path
        ))
        
        # Detection task
        self.register_task(TaskInfo(
            task_type=TaskType.DETECTION,
            name="目标检测",
            description="检测图像中的多个对象并用边界框标记它们的位置。适合识别和定位图像中的特定对象，如人员检测、车辆识别、物体计数等。",
            example_image=None
        ))
        
        # Segmentation task
        self.register_task(TaskInfo(
            task_type=TaskType.SEGMENTATION,
            name="语义分割", 
            description="为图像中的每个像素分配类别标签，将图像分割成不同的语义区域。适合需要精确边界的应用，如医学图像分析、遥感图像处理等。",
            example_image=None
        ))
        
        # Instance Segmentation task
        self.register_task(TaskInfo(
            task_type=TaskType.INSTANCE_SEGMENTATION,
            name="实例分割",
            description="不仅识别图像中的对象类别，还能区分同一类别的不同实例，为每个实例提供精确的像素级分割。适合需要区分个体对象的场景。",
            example_image=None
        ))
        
        # Keypoint task
        self.register_task(TaskInfo(
            task_type=TaskType.KEYPOINT,
            name="关键点检测",
            description="检测并定位对象上的特定关键点，如人体姿态的关节点。适合姿态估计、动作分析、人机交互等应用场景。",
            example_image=None
        ))
        
        # Oriented Detection task
        self.register_task(TaskInfo(
            task_type=TaskType.ORIENTED_DETECTION,
            name="有向边界框检测",
            description="使用可旋转的边界框检测对象，适合检测具有任意方向的对象。常用于文本检测、遥感图像分析、工业零件检测等场景。",
            example_image=None
        ))
    
    def register_task(self, task_info: TaskInfo):
        """
        Register a task type information.
        
        Args:
            task_info: Task information to register
        """
        self._tasks[task_info.task_type] = task_info
    
    def get_task_info(self, task_type: TaskType) -> Optional[TaskInfo]:
        """
        Get task information by task type.
        
        Args:
            task_type: The task type to get information for
            
        Returns:
            Task information if found, None otherwise
        """
        return self._tasks.get(task_type)
    
    def get_all_tasks(self) -> List[TaskInfo]:
        """
        Get all registered task information.
        
        Returns:
            List of all task information in registration order
        """
        # Return in a specific order for UI consistency
        ordered_types = [
            TaskType.CLASSIFICATION,
            TaskType.DETECTION,
            TaskType.SEGMENTATION,
            TaskType.INSTANCE_SEGMENTATION,
            TaskType.KEYPOINT,
            TaskType.ORIENTED_DETECTION
        ]
        
        tasks = []
        for task_type in ordered_types:
            if task_type in self._tasks:
                tasks.append(self._tasks[task_type])
        
        # Add any remaining tasks not in the ordered list
        for task_type, task_info in self._tasks.items():
            if task_type not in ordered_types:
                tasks.append(task_info)
        
        return tasks
    
    def get_task_types(self) -> List[TaskType]:
        """
        Get all registered task types.
        
        Returns:
            List of task types
        """
        return [task.task_type for task in self.get_all_tasks()]
    
    def get_task_names(self) -> List[str]:
        """
        Get display names of all registered tasks.
        
        Returns:
            List of task display names
        """
        return [task.name for task in self.get_all_tasks()]
    
    def search_tasks(self, query: str) -> List[TaskInfo]:
        """
        Search tasks by name or description.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching task information
        """
        query = query.lower()
        matches = []
        
        for task_info in self.get_all_tasks():
            if (query in task_info.name.lower() or 
                query in task_info.description.lower()):
                matches.append(task_info)
        
        return matches
    
    def is_task_registered(self, task_type: TaskType) -> bool:
        """
        Check if a task type is registered.
        
        Args:
            task_type: Task type to check
            
        Returns:
            True if task is registered, False otherwise
        """
        return task_type in self._tasks
    
    def get_task_count(self) -> int:
        """Get the number of registered tasks."""
        return len(self._tasks)
    
    def get_task_by_name(self, name: str) -> Optional[TaskInfo]:
        """
        Get task information by display name.
        
        Args:
            name: Display name to search for
            
        Returns:
            Task information if found, None otherwise
        """
        for task_info in self._tasks.values():
            if task_info.name == name:
                return task_info
        return None
    
    def update_task_example_image(self, task_type: TaskType, image_path: str):
        """
        Update the example image for a task type.
        
        Args:
            task_type: Task type to update
            image_path: Path to the example image
        """
        if task_type in self._tasks:
            self._tasks[task_type].example_image = image_path
    
    def remove_task(self, task_type: TaskType):
        """
        Remove a task type from the registry.
        
        Args:
            task_type: Task type to remove
        """
        if task_type in self._tasks:
            del self._tasks[task_type]
    
    def __str__(self) -> str:
        return f"TaskTypeProvider({self.get_task_count()} tasks registered)"
    
    def __repr__(self) -> str:
        return self.__str__()
