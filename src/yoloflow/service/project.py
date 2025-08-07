"""
Project class for YOLOFlow.
Manages individual project operations and folder structure.
"""

from pathlib import Path
from typing import Optional, List
from datetime import datetime
from .project_config import ProjectConfig


class Project:
    """
    表示一个YOLO项目的类。
    负责项目文件夹结构的创建和管理，以及项目配置的操作。
    """
    
    # 项目必需的文件夹结构
    REQUIRED_FOLDERS = [
        "dataset",    # 存放数据集
        "model",      # 存放模型权重文件
        "pretrain",   # 存放预训练权重
        "runs",       # 存放训练日志和结果
    ]
    
    def __init__(self, project_path: Path):
        """
        初始化项目。
        
        Args:
            project_path: 项目根目录路径
        """
        self.path = Path(project_path)
        self.config = ProjectConfig(self.path)
        
        # 验证项目结构
        if not self._is_valid_project():
            raise ValueError(f"Invalid project structure at {self.path}")
    
    @classmethod
    def create_new(cls, project_path: Path, project_name: str, task_type: str = "detect") -> "Project":
        """
        创建新项目。
        
        Args:
            project_path: 项目根目录路径
            project_name: 项目名称
            task_type: 任务类型 (detect, classify, segment, pose, obb)
        
        Returns:
            Project实例
        """
        project_path = Path(project_path)
        
        # 创建项目目录
        project_path.mkdir(parents=True, exist_ok=True)
        
        # 创建必需的文件夹结构
        for folder in cls.REQUIRED_FOLDERS:
            (project_path / folder).mkdir(exist_ok=True)
        
        # 创建项目实例（这会自动创建配置文件）
        project = cls(project_path)
        
        # 设置项目信息
        project.config.project_name = project_name
        project.config.task_type = task_type
        
        return project
    
    def _is_valid_project(self) -> bool:
        """检查是否是有效的项目结构。"""
        # 检查项目目录是否存在
        if not self.path.exists():
            return False
        
        # 检查配置文件是否存在
        config_file = self.path / "yoloflow.toml"
        if not config_file.exists():
            # 如果配置文件不存在但有必需文件夹，可能是旧项目，尝试创建配置
            if all((self.path / folder).exists() for folder in self.REQUIRED_FOLDERS):
                return True
            return False
        
        return True
    
    def ensure_folder_structure(self) -> None:
        """确保项目文件夹结构完整。"""
        for folder in self.REQUIRED_FOLDERS:
            folder_path = self.path / folder
            folder_path.mkdir(exist_ok=True)
    
    @property
    def name(self) -> str:
        """项目名称。"""
        return self.config.project_name
    
    @property
    def task_type(self) -> str:
        """任务类型。"""
        return self.config.task_type
    
    @property
    def description(self) -> str:
        """项目描述。"""
        return self.config.description
    
    @property
    def dataset_path(self) -> Path:
        """数据集目录路径。"""
        return self.path / "dataset"
    
    @property
    def model_path(self) -> Path:
        """模型目录路径。"""
        return self.path / "model"
    
    @property
    def pretrain_path(self) -> Path:
        """预训练权重目录路径。"""
        return self.path / "pretrain"
    
    @property
    def runs_path(self) -> Path:
        """训练结果目录路径。"""
        return self.path / "runs"
    
    def get_datasets(self) -> List[str]:
        """获取可用的数据集列表。"""
        return self.config.available_datasets
    
    def get_models(self) -> List[str]:
        """获取可用的模型列表。"""
        return self.config.available_models
    
    def get_current_dataset(self) -> Optional[str]:
        """获取当前选择的数据集。"""
        return self.config.current_dataset
    
    def get_current_model(self) -> Optional[str]:
        """获取当前选择的模型。"""
        return self.config.current_model
    
    def set_current_dataset(self, dataset_name: Optional[str]) -> None:
        """设置当前数据集。"""
        self.config.current_dataset = dataset_name
    
    def set_current_model(self, model_name: Optional[str]) -> None:
        """设置当前模型。"""
        self.config.current_model = model_name
    
    def add_dataset(self, dataset_name: str) -> None:
        """添加数据集。"""
        self.config.add_dataset(dataset_name)
    
    def add_model(self, model_name: str) -> None:
        """添加模型。"""
        self.config.add_model(model_name)
    
    def get_training_parameters(self) -> dict:
        """获取训练参数。"""
        return self.config.training_parameters
    
    def update_last_accessed(self) -> None:
        """更新最后访问时间。"""
        # 这个方法将由ProjectManager调用来更新数据库中的最后访问时间
        pass
    
    def __str__(self) -> str:
        return f"Project(name='{self.name}', path='{self.path}', task='{self.task_type}')"
    
    def __repr__(self) -> str:
        return self.__str__()
