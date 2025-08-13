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
    
    # TODO：后端位置等其他非抽象类定义的属性
    
    @classmethod
    def from_backend(cls, backend: BackendBase) -> 'BackendInfo':
        """从BackendBase实例创建BackendInfo"""
        
        return cls(
            name=backend.name,
            version=backend.version,
            version_code=backend.version_code,
            author=backend.author,
            description=backend.description,
            linked_page=backend.linked_page,
        )
