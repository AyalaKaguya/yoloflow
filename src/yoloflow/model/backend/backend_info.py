"""
后端信息数据类
用于存储后端的所有相关信息
"""

from dataclasses import dataclass, field
from typing import Optional, Set, TYPE_CHECKING
from ..enums import BackendUnavailableReason, TaskType
from ..start_up import ModelInfo
from .backend_base import BackendBase

if TYPE_CHECKING:
    from .backend_base import BackendBase


@dataclass
class BackendInfo:
    """后端信息数据类，包含后端的所有相关信息"""
    
    name: str
    """后端名称"""
    
    version: str
    """后端版本"""
    
    version_code: int
    """后端版本号，供给yoloflow判断"""
    
    author: str
    """后端作者"""
    
    description: Optional[str] = None
    """后端描述"""
    
    linked_page: Optional[str] = None
    """后端链接网页"""
    
    # ============================== 可用性信息 ==============================
    is_available: bool = False
    """后端是否可用"""
    
    unavailable_reason: Optional[BackendUnavailableReason] = None
    """不可用的原因（当is_available为False时）"""
    
    # ============================== 环境配置信息 ==============================
    executable: str = ""
    """后端执行的命令"""
    
    extra_params: Optional[list[str]] = field(default_factory=list)
    """后端执行的额外参数"""
    
    # ============================== 后端能力信息 ==============================
    available_tasks: Set[TaskType] = field(default_factory=set)
    """后端支持的任务类型"""
    
    available_models: Set[ModelInfo] = field(default_factory=set)
    """后端支持的模型信息"""
    
    # ============================== 后端管理信息 ==============================
    module_path: Optional[str] = None
    """后端模块路径"""

    is_installed: bool = False
    """后端是否已安装"""
    
    instance: Optional[BackendBase] = field(default=None, repr=False)
    """后端实例，这个属性不要导出"""

    @classmethod
    def from_backend(cls, backend: BackendBase, yoloflow_version: str = "1.0.0", module_path: Optional[str] = None) -> 'BackendInfo':
        """从BackendBase实例创建BackendInfo"""
        
        # 检查可用性
        is_available, unavailable_reason = backend.is_available(yoloflow_version)
        
        return cls(
            name=backend.name,
            version=backend.version,
            version_code=backend.version_code,
            author=backend.author,
            description=backend.description,
            linked_page=backend.linked_page,
            is_available=is_available,
            unavailable_reason=unavailable_reason,
            executable=backend.executable,
            extra_params=backend.extra_params.copy() if backend.extra_params else [],
            available_tasks=backend.available_tasks.copy() if backend.available_tasks else set(),
            available_models=backend.available_models.copy() if backend.available_models else set(),
            module_path=module_path,
            is_installed=True,  # 如果能创建实例说明已安装
            instance=backend
        )
    
    def get_display_name(self) -> str:
        """获取显示名称（名称 + 版本）"""
        return f"{self.name} v{self.version}"
    
    def get_full_command(self) -> list[str]:
        """获取完整的执行命令"""
        cmd = ["uv", "run", self.executable]
        if self.extra_params:
            cmd.extend(self.extra_params)
        assert self.instance is not None
        cmd = self.instance.process_cli_args(cmd)
        return cmd
    
    def supports_task(self, task_type: TaskType) -> bool:
        """检查是否支持指定的任务类型"""
        return task_type in self.available_tasks
    
    def supports_model(self, model: ModelInfo) -> bool:
        """检查是否支持指定的模型"""
        return model in self.available_models
    
    def to_dict(self) -> dict:
        """转换为字典格式，用于保存到toml文件"""
        return {
            "name": self.name,
            "version": self.version,
            "version_code": self.version_code,
            "author": self.author,
            "description": self.description,
            "linked_page": self.linked_page,
            "executable": self.executable,
            "extra_params": self.extra_params,
            "available_tasks": [task.value for task in self.available_tasks],
            "module_path": self.module_path,
            "is_installed": self.is_installed
        }
    
    def __str__(self) -> str:
        return f"{self.get_display_name()} by {self.author} v{self.version}"
