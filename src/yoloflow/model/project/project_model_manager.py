"""
Manager for all models within a project.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..enums import TaskType
from .project_config import ProjectConfig
from .project_model_info import ProjectModelInfo


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
        
        # 同步训练模型
        self._sync_trained_models()
    
    def _sync_trained_models(self):
        """同步训练模型信息"""
        # 获取文件系统中的训练模型
        filesystem_models = set()
        if self.model_dir.exists():
            for model_file in self.model_dir.glob("*.pt"):
                filesystem_models.add(model_file.name)
        
        # 获取配置中的训练模型
        config_models = set()
        for model_info in self.config.model_details:
            if model_info.source == "plan_created":
                config_models.add(model_info.filename)
        
        # 移除配置中存在但文件系统中不存在的训练模型
        for model in config_models - filesystem_models:
            self.config.remove_model(model)
        
        # 如果有变化，保存配置
        if config_models - filesystem_models:
            self.config.save()
    
    def get_pretrained_models(self) -> List[ProjectModelInfo]:
        """
        Get list of pretrained model information.
        
        Returns:
            List of ProjectModelInfo objects for pretrained models, synchronized between config and filesystem
        """
        # 从配置中获取预训练模型列表
        config_models = set(self.config.pretrained_models)
        
        # 从文件系统获取实际存在的模型
        filesystem_models = set()
        if self.pretrain_dir.exists():
            for model_file in self.pretrain_dir.glob("*.pt"):
                filesystem_models.add(model_file.name)
        
        # 同步配置和文件系统
        # 1. 移除配置中存在但文件系统中不存在的模型
        for model in config_models - filesystem_models:
            self.config.remove_model(model)
        
        # 2. 添加文件系统中存在但配置中不存在的模型
        for model in filesystem_models - config_models:
            # 自动推断模型信息
            model_name = model.replace('.pt', '').replace('_', ' ').title()
            model_info = ProjectModelInfo(
                name=model_name,
                filename=model,
                description=f"Auto-discovered model: {model_name}",
                parameters="",  # 未知参数量
                task_type=self.task_type,
                source="imported"
            )
            self.config.add_model(model_info)
        
        # 如果有变化，保存配置
        if (config_models - filesystem_models) or (filesystem_models - config_models):
            self.config.save()
        
        # 返回文件系统中实际存在的模型的ProjectModelInfo对象
        result = []
        for model_info in self.config.model_details:
            if (model_info.source in ["imported", "project_creation"] and 
                model_info.filename in filesystem_models):
                result.append(model_info)
        
        # 按文件名排序
        return sorted(result, key=lambda x: x.filename)
    
    def get_trained_models(self) -> List[ProjectModelInfo]:
        """
        Get list of trained model information.
        
        Returns:
            List of ProjectModelInfo objects for trained models
        """
        # 获取文件系统中的训练模型文件
        filesystem_models = set()
        if self.model_dir.exists():
            for model_file in self.model_dir.glob("*.pt"):
                filesystem_models.add(model_file.name)
        
        # 获取配置中的训练模型信息
        result = []
        for model_info in self.config.model_details:
            if (model_info.source == "plan_created" and 
                model_info.filename in filesystem_models):
                result.append(model_info)
        
        # 对于文件系统中存在但配置中不存在的训练模型，自动添加
        config_trained_models = {info.filename for info in result}
        for model_filename in filesystem_models - config_trained_models:
            # 自动推断模型信息
            model_name = model_filename.replace('.pt', '').replace('_', ' ').title()
            model_info = ProjectModelInfo(
                name=model_name,
                filename=model_filename,
                description=f"Auto-discovered trained model: {model_name}",
                parameters="",
                task_type=self.task_type,
                source="plan_created"
            )
            self.config.add_model(model_info)
            result.append(model_info)
        
        # 如果有新增模型，保存配置
        if filesystem_models - config_trained_models:
            self.config.save()
        
        # 按文件名排序
        return sorted(result, key=lambda x: x.filename)
    
    def add_pretrained_model(
        self,
        source_path: Union[str, Path],
        model_name: str,
        description: str = "",
        parameters: str = "",
        task_type: Optional[TaskType] = None,
        filename: Optional[str] = None
    ) -> ProjectModelInfo:
        """
        Add a pretrained model to the project with detailed information.
        
        Args:
            source_path: Path to source model file
            model_name: Display name for the model (e.g., "YOLO11 Nano")
            description: Description of the model
            parameters: Number of parameters in the model
            task_type: Task type this model supports (defaults to project task type)
            filename: Custom filename (defaults to source filename)
            
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
        if filename:
            if not filename.endswith('.pt'):
                filename += '.pt'
            target_name = filename
        else:
            target_name = source_path.name
        
        target_path = self.pretrain_dir / target_name
        
        # Check if model already exists
        if target_path.exists():
            raise ValueError(f"Pretrained model '{target_name}' already exists")
        
        # Copy model file
        import shutil
        shutil.copy2(source_path, target_path)
        
        # Create model info with detailed information
        model_info = ProjectModelInfo(
            name=model_name,
            filename=target_name,
            description=description,
            parameters=parameters,
            task_type=task_type or self.task_type,
            source="imported"
        )
        
        # Add to config
        self.config.add_model(model_info)
        self.config.save()
        
        return model_info
    
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
            # Remove from config
            self.config.remove_model(model_name)
            self.config.save()
            return True
        return False
    
    def add_trained_model(
        self,
        source_path: Union[str, Path],
        plan_name: str,
        model_name: str,
        description: str = "",
        parameters: str = "",
        filename: Optional[str] = None
    ) -> str:
        """
        Add a trained model to the project with detailed information.
        
        Args:
            source_path: Path to source model file
            plan_name: Name of the training plan that created this model
            model_name: Display name for the model
            description: Description of the model
            parameters: Number of parameters in the model
            filename: Custom filename (defaults to source filename)
            
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
        if filename:
            if not filename.endswith('.pt'):
                filename += '.pt'
            target_name = filename
        else:
            target_name = source_path.name
        
        target_path = self.model_dir / target_name
        
        # Check if model already exists
        if target_path.exists():
            raise ValueError(f"Trained model '{target_name}' already exists")
        
        # Copy model file
        import shutil
        shutil.copy2(source_path, target_path)
        
        # Create model info with detailed information
        model_info = ProjectModelInfo(
            name=model_name,
            filename=target_name,
            description=description or f"Model trained from plan: {plan_name}",
            parameters=parameters,
            task_type=self.task_type,
            source="plan_created"
        )
        
        # Add to config
        self.config.add_model(model_info)
        self.config.save()
        
        return target_name
    
    def add_model_from_info(self, model_info: ProjectModelInfo, source_path: Union[str, Path]) -> ProjectModelInfo:
        """
        Add a model using a ProjectModelInfo instance.
        
        Args:
            model_info: Complete model information
            source_path: Path to source model file
            
        Returns:
            Name of the added model file
            
        Raises:
            FileNotFoundError: If source file doesn't exist
            ValueError: If model already exists
        """
        source_path = Path(source_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Source model file not found: {source_path}")
        
        # Determine target directory based on source
        if model_info.source in ["imported", "project_creation"]:
            target_dir = self.pretrain_dir
        else:
            target_dir = self.model_dir
        
        target_path = target_dir / model_info.filename
        
        # Check if model already exists
        if target_path.exists():
            raise ValueError(f"Model '{model_info.filename}' already exists")
        
        # Copy model file
        import shutil
        shutil.copy2(source_path, target_path)
        
        # Add to config
        self.config.add_model(model_info)
        self.config.save()
        
        return model_info
    
    def get_pretrained_model_path(self, model_name: str) -> Optional[Path]:
        """Get absolute path to pretrained model."""
        model_path = self.pretrain_dir / model_name
        return model_path if model_path.exists() else None
    
    def get_trained_model_path(self, model_name: str) -> Optional[Path]:
        """Get absolute path to trained model."""
        model_path = self.model_dir / model_name
        return model_path if model_path.exists() else None
    
    def get_pretrained_model_filenames(self) -> List[str]:
        """
        Get list of pretrained model filenames (compatibility method).
        
        Returns:
            List of pretrained model filenames
        """
        return [model.filename for model in self.get_pretrained_models()]
    
    def get_trained_model_filenames(self) -> List[str]:
        """
        Get list of trained model filenames (compatibility method).
        
        Returns:
            List of trained model filenames
        """
        return [model.filename for model in self.get_trained_models()]
    
    def get_model_info_by_filename(self, filename: str) -> Optional[ProjectModelInfo]:
        """
        Get model information by filename.
        
        Args:
            filename: Model filename to search for
            
        Returns:
            ProjectModelInfo object if found, None otherwise
        """
        # Search in pretrained models
        for model in self.get_pretrained_models():
            if model.filename == filename:
                return model
        
        # Search in trained models
        for model in self.get_trained_models():
            if model.filename == filename:
                return model
        
        return None
    
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
            "pretrained_model_list": [model.filename for model in pretrained_models],
            "trained_model_list": [model.filename for model in trained_models],
            "pretrained_model_info": [model.to_dict() for model in pretrained_models],
            "trained_model_info": [model.to_dict() for model in trained_models],
            "config_pretrained_models": self.config.pretrained_models,
            "available_models": self.config.available_models,
            "model_details": [info.to_dict() for info in self.config.model_details]
        }
    
    def __str__(self) -> str:
        summary = self.get_model_summary()
        return f"ProjectModelManager({summary['pretrained_models']} pretrained, {summary['trained_models']} trained)"
    
    def __repr__(self) -> str:
        return self.__str__()
