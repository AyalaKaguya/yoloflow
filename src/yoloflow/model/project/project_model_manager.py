"""
Manager for all models within a project.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..enums import TaskType
from .project_config import ProjectConfig


class ProjectModelManager:
    """
    Manager for all models within a project.
    
    Handles both pretrained models and trained models, as well as
    training plans through the ProjectPlanManager.
    """
    
    def __init__(self, project_path: Path, project_config: ProjectConfig):
        """
        Initialize project model manager.
        
        Args:
            project_path: Path to the project directory
            project_config: Project configuration instance
        """
        self.project_path = Path(project_path)
        self.config = project_config
        self.task_type = project_config.task_type
        self.pretrain_dir = self.project_path / "pretrain"
        self.model_dir = self.project_path / "model"
        
        # Ensure directories exist
        self.pretrain_dir.mkdir(exist_ok=True)
        self.model_dir.mkdir(exist_ok=True)
        
        # 初始化时同步配置和文件系统
        self._sync_config_with_filesystem()
    
    def _sync_config_with_filesystem(self):
        """同步配置和文件系统中的模型信息"""
        # 触发 get_pretrained_models 来执行同步逻辑
        self.get_pretrained_models()
        
        # 同步训练模型（如果需要的话）
        # TODO: 如果以后需要在配置中跟踪训练模型，可以在这里添加逻辑
    
    def get_pretrained_models(self) -> List[str]:
        """
        Get list of pretrained model files.
        
        Returns:
            List of pretrained model filenames, synchronized between config and filesystem
        """
        # 从配置中获取模型列表
        config_models = set(self.config.pretrained_models)
        
        # 从文件系统获取实际存在的模型
        filesystem_models = set()
        if self.pretrain_dir.exists():
            for model_file in self.pretrain_dir.glob("*.pt"):
                filesystem_models.add(model_file.name)
        
        # 同步配置和文件系统
        # 1. 移除配置中存在但文件系统中不存在的模型
        for model in config_models - filesystem_models:
            self.config.remove_pretrained_model(model)
        
        # 2. 添加文件系统中存在但配置中不存在的模型
        for model in filesystem_models - config_models:
            self.config.add_pretrained_model(model)
        
        # 如果有变化，保存配置
        if (config_models - filesystem_models) or (filesystem_models - config_models):
            self.config.save()
        
        # 返回文件系统中实际存在的模型列表（已排序）
        return sorted(list(filesystem_models))
    
    def get_trained_models(self) -> List[str]:
        """
        Get list of trained model files.
        
        Returns:
            List of trained model filenames
        """
        models = []
        if self.model_dir.exists():
            for model_file in self.model_dir.glob("*.pt"):
                models.append(model_file.name)
        return sorted(models)
    
    def add_pretrained_model(self, source_path: Union[str, Path], model_name: Optional[str] = None) -> str:
        """
        Add a pretrained model to the project.
        
        Args:
            source_path: Path to source model file
            model_name: Optional custom name for the model
            
        Returns:
            Name of the added model file
            
        Raises:
            FileNotFoundError: If source file doesn't exist
            ValueError: If model already exists
        """
        source_path = Path(source_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Source model file not found: {source_path}")
        
        # Determine target filename
        if model_name:
            if not model_name.endswith('.pt'):
                model_name += '.pt'
            target_name = model_name
        else:
            target_name = source_path.name
        
        target_path = self.pretrain_dir / target_name
        
        # Check if model already exists
        if target_path.exists():
            raise ValueError(f"Pretrained model '{target_name}' already exists")
        
        # Copy model file
        import shutil
        shutil.copy2(source_path, target_path)
        
        # 将模型信息同步到项目配置中
        self.config.add_pretrained_model(target_name)
        self.config.save()
        
        return target_name
    
    def remove_pretrained_model(self, model_name: str) -> bool:
        """
        Remove a pretrained model.
        
        Args:
            model_name: Name of the model to remove
            
        Returns:
            True if model was removed, False if not found
        """
        model_path = self.pretrain_dir / model_name
        if model_path.exists():
            model_path.unlink()
            # 从项目配置中移除模型信息
            self.config.remove_pretrained_model(model_name)
            self.config.save()
            return True
        return False
    
    def get_pretrained_model_path(self, model_name: str) -> Optional[Path]:
        """Get absolute path to pretrained model."""
        model_path = self.pretrain_dir / model_name
        return model_path if model_path.exists() else None
    
    def get_trained_model_path(self, model_name: str) -> Optional[Path]:
        """Get absolute path to trained model."""
        model_path = self.model_dir / model_name
        return model_path if model_path.exists() else None
    
    def get_model_summary(self) -> Dict[str, Any]:
        """
        Get summary of models.
        
        Returns:
            Dictionary with model counts and information from both filesystem and config
        """
        pretrained_models = self.get_pretrained_models()
        trained_models = self.get_trained_models()
        
        return {
            "pretrained_models": len(pretrained_models),
            "trained_models": len(trained_models),
            "pretrained_model_list": pretrained_models,
            "trained_model_list": trained_models,
            "config_pretrained_models": self.config.pretrained_models,
            "current_model": self.config.current_model
        }
    
    def __str__(self) -> str:
        summary = self.get_model_summary()
        return f"ProjectModelManager({summary['pretrained_models']} pretrained, {summary['trained_models']} trained)"
    
    def __repr__(self) -> str:
        return self.__str__()
