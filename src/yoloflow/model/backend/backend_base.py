from abc import ABC, abstractmethod
from typing import Optional
from ..enums import BackendUnavailableReason, TaskType
from ..start_up import ModelInfo, TaskInfo


class BackendBase(ABC):
    """后端基类，所有后端都应当继承自此类"""

    # ============================== 基础信息 ==============================

    @property
    @abstractmethod
    def name(self) -> str:
        """该属性应当返回后端的名称"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """该属性应当返回后端的版本"""
        pass

    @property
    @abstractmethod
    def version_code(self) -> int:
        """该属性应当返回后端的版本号，供给yoloflow判断"""
        pass

    @property
    @abstractmethod
    def author(self) -> str:
        """该属性应当返回后端的作者"""
        pass

    @property
    def description(self) -> str:
        """该属性应当返回后端的描述"""
        return ""

    @property
    def linked_page(self) -> str:
        """该属性应当返回后端的链接网页"""
        return ""

    @abstractmethod
    def is_available(self, yoloflow_version: str) -> tuple[bool, BackendUnavailableReason | None]:
        """该方法应当判断后端是否可用"""
        pass

    # ============================== 环境配置 ==============================
    
    # 一个项目的根目录下除了有要以模块形式加载的__init__.py以外，还要有完整的一个pyproject.toml、src
    
    def pre_install(self, backend_dir: str) -> None:
        """yoloflow会使用uv venv创建虚拟环境，但是此时还未正式开始安装依赖，你可以执行一些前置操作"""
        pass
    
    def post_install(self, backend_dir: str) -> None:
        """后端在安装完成过后可以进行一些检查以判断后端是否可用，通过抛出异常可以使得yoloflow认为后端存在问题"""
        pass

    @property
    @abstractmethod
    def executable(self) -> str:
        """后端执行的命令，后续yoloflow会以`uv run <executable> [params]`来调用和启动后端"""
        pass
    
    @property
    def extra_params(self) -> list[str]:
        """后端执行的额外参数，后续yoloflow会以`uv run <executable> [params]`来调用和启动后端"""
        return []
    
    # ============================== 后端能力 ==============================
    
    @property
    @abstractmethod
    def available_tasks(self) -> set[TaskType]:
        """返回后端支持的任务类型"""
        pass

    @property
    @abstractmethod
    def available_models(self) -> set[ModelInfo]:
        """返回后端支持的模型信息"""
        pass
    
    @abstractmethod
    def get_download_link(self, model: ModelInfo) -> Optional[str]:
        """获取模型的下载链接"""
        pass

    def process_cli_args(self, args: list[str]) -> list[str]:
        """处理并返回命令行参数，默认不做修改"""
        return args
    

