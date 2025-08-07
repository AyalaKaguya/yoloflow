"""
Project configuration management for YOLOFlow.
Handles reading and writing project configuration files (yoloflow.toml).
"""

import toml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class ProjectConfig:
    """
    管理项目配置文件 (yoloflow.toml) 的类。
    负责项目的详细设置，包括数据集、模型、训练参数等。
    """
    
    def __init__(self, project_path: Path):
        """
        初始化项目配置。
        
        Args:
            project_path: 项目根目录路径
        """
        self.project_path = Path(project_path)
        self.config_file = self.project_path / "yoloflow.toml"
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件，如果不存在则创建默认配置。"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return toml.load(f)
        else:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """创建默认配置。"""
        default_config = {
            "project": {
                "name": self.project_path.name,
                "task_type": "detect",  # detect, classify, segment, pose, obb
                "created_at": datetime.now().isoformat(),
                "description": "",
            },
            "datasets": {
                "available": [],
                "current": None,
            },
            "models": {
                "available": [],
                "current": None,
                "training_history": [],
            },
            "training": {
                "parameters": {
                    "epochs": "100",
                    "batch_size": "16",
                    "img_size": "640",
                    "lr": "0.01",
                    "optimizer": "SGD",
                },
                "custom_parameters": {},  # 用户自定义的训练参数
            },
        }
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> None:
        """保存配置到文件。"""
        if config is not None:
            self._config = config
        
        # 确保目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            toml.dump(self._config, f)
    
    # Project Info
    @property
    def project_name(self) -> str:
        """项目名称。"""
        return self._config["project"]["name"]
    
    @project_name.setter
    def project_name(self, value: str) -> None:
        self._config["project"]["name"] = value
        self.save_config()
    
    @property
    def task_type(self) -> str:
        """任务类型。"""
        return self._config["project"]["task_type"]
    
    @task_type.setter
    def task_type(self, value: str) -> None:
        self._config["project"]["task_type"] = value
        self.save_config()
    
    @property
    def description(self) -> str:
        """项目描述。"""
        return self._config["project"]["description"]
    
    @description.setter
    def description(self, value: str) -> None:
        self._config["project"]["description"] = value
        self.save_config()
    
    # Datasets
    @property
    def available_datasets(self) -> List[str]:
        """可用的数据集列表。"""
        return self._config["datasets"]["available"]
    
    @property
    def current_dataset(self) -> Optional[str]:
        """当前选择的数据集。"""
        return self._config["datasets"]["current"]
    
    @current_dataset.setter
    def current_dataset(self, value: Optional[str]) -> None:
        self._config["datasets"]["current"] = value
        self.save_config()
    
    def add_dataset(self, dataset_name: str) -> None:
        """添加数据集。"""
        if dataset_name not in self._config["datasets"]["available"]:
            self._config["datasets"]["available"].append(dataset_name)
            self.save_config()
    
    def remove_dataset(self, dataset_name: str) -> None:
        """移除数据集。"""
        if dataset_name in self._config["datasets"]["available"]:
            self._config["datasets"]["available"].remove(dataset_name)
            # 如果移除的是当前数据集，清空当前选择
            if self._config["datasets"]["current"] == dataset_name:
                self._config["datasets"]["current"] = None
            self.save_config()
    
    # Models
    @property
    def available_models(self) -> List[str]:
        """可用的模型列表。"""
        return self._config["models"]["available"]
    
    @property
    def current_model(self) -> Optional[str]:
        """当前选择的模型。"""
        return self._config["models"]["current"]
    
    @current_model.setter
    def current_model(self, value: Optional[str]) -> None:
        self._config["models"]["current"] = value
        self.save_config()
    
    def add_model(self, model_name: str) -> None:
        """添加模型。"""
        if model_name not in self._config["models"]["available"]:
            self._config["models"]["available"].append(model_name)
            self.save_config()
    
    def add_training_record(self, record: Dict[str, Any]) -> None:
        """添加训练记录。"""
        self._config["models"]["training_history"].append(record)
        self.save_config()
    
    # Training Parameters
    @property
    def training_parameters(self) -> Dict[str, str]:
        """训练参数。"""
        return self._config["training"]["parameters"]
    
    def set_training_parameter(self, key: str, value: str) -> None:
        """设置训练参数。"""
        self._config["training"]["parameters"][key] = value
        self.save_config()
    
    def set_custom_parameter(self, key: str, value: str) -> None:
        """设置自定义参数（用于将来界面直接修改）。"""
        self._config["training"]["custom_parameters"][key] = value
        self.save_config()
    
    @property
    def custom_parameters(self) -> Dict[str, str]:
        """自定义参数。"""
        return self._config["training"]["custom_parameters"]
    
    def get_full_config(self) -> Dict[str, Any]:
        """获取完整配置。"""
        return self._config.copy()
