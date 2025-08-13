

"""
后端管理器
负责管理所有后端模块的加载、安装、卸载、查询等功能
"""

import os
import sys
import toml
import shutil
import subprocess
import importlib.util
from pathlib import Path
from typing import List, Dict, Optional, Set
from threading import Thread
from dataclasses import asdict

from ..model.backend import BackendBase, BackendInfo
from ..model.enums import TaskType
from ..model.start_up import ModelInfo, ModelSelector
from ..__version__ import __version__ as yoloflow_version

class BackendManager:
    """后端管理器类"""
    
    def __init__(self, backends_dir: Optional[str] = None):
        """初始化后端管理器
        
        Args:
            backends_dir: 后端目录路径，默认为当前工作目录下的backends文件夹
        """
        self.backends_dir = Path(backends_dir) if backends_dir else Path.cwd() / "backends"
        self.backends_dir.mkdir(exist_ok=True)
        
        # 后端信息存储
        self._backend_infos: Dict[str, BackendInfo] = {}
        self._loaded_backends: Dict[str, BackendBase] = {}
        
        # 模型选择器
        self.model_selector = ModelSelector(self)
        
        # 扫描后端目录
        self._scan_backend_directories()
    
    def _scan_backend_directories(self):
        """扫描后端目录，发现可用的后端"""
        if not self.backends_dir.exists():
            return
        
        for backend_dir in self.backends_dir.iterdir():
            if backend_dir.is_dir() and (backend_dir / "__init__.py").exists():
                backend_name = backend_dir.name
                
                # 检查是否有对应的toml文件
                toml_file = self.backends_dir / f"{backend_name}.toml"
                if toml_file.exists():
                    try:
                        info = self._load_backend_info_from_toml(toml_file)
                        info.module_path = str(backend_dir)
                        self._backend_infos[backend_name] = info
                    except Exception as e:
                        print(f"Failed to load backend info from {toml_file}: {e}")
                else:
                    # 创建基础的BackendInfo
                    info = BackendInfo(
                        name=backend_name,
                        version="unknown",
                        version_code=0,
                        author="unknown",
                        module_path=str(backend_dir),
                        is_installed=False
                    )
                    self._backend_infos[backend_name] = info
    
    def _load_backend_info_from_toml(self, toml_file: Path) -> BackendInfo:
        """从toml文件加载后端信息"""
        data = toml.load(toml_file)
        
        available_tasks = set()
        if data.get("available_tasks"):
            available_tasks = {TaskType(task) for task in data["available_tasks"]}
        
        return BackendInfo(
            name=data.get("name", ""),
            version=data.get("version", ""),
            version_code=data.get("version_code", 0),
            author=data.get("author", ""),
            description=data.get("description"),
            linked_page=data.get("linked_page"),
            executable=data.get("executable", ""),
            extra_params=data.get("extra_params", []),
            available_tasks=available_tasks,
            module_path=data.get("module_path"),
            is_installed=data.get("is_installed", False)
        )
    
    def _save_backend_info_to_toml(self, backend_name: str, info: BackendInfo):
        """保存后端信息到toml文件"""
        toml_file = self.backends_dir / f"{backend_name}.toml"
        
        data = info.to_dict()
        # 移除不需要序列化的字段
        data.pop("instance", None)
        
        with open(toml_file, 'w', encoding='utf-8') as f:
            toml.dump(data, f)
    
    def get_available_backends(self) -> List[str]:
        """获取可用的后端名称列表"""
        return list(self._backend_infos.keys())
    
    def get_backend_info(self, backend_name: str) -> Optional[BackendInfo]:
        """获取指定后端的信息"""
        return self._backend_infos.get(backend_name)
    
    def get_all_backend_infos(self) -> List[BackendInfo]:
        """获取所有后端信息"""
        return list(self._backend_infos.values())
    
    def load_backend(self, backend_name: str) -> bool:
        """加载指定的后端模块
        
        Args:
            backend_name: 后端名称
            
        Returns:
            bool: 是否加载成功
        """
        if backend_name in self._loaded_backends:
            return True
        
        backend_info = self._backend_infos.get(backend_name)
        if not backend_info or not backend_info.module_path:
            return False
        
        try:
            # 动态导入后端模块
            module_path = Path(backend_info.module_path)
            spec = importlib.util.spec_from_file_location(
                backend_name, 
                module_path / "__init__.py"
            )
            
            if spec is None or spec.loader is None:
                return False
            
            module = importlib.util.module_from_spec(spec)
            
            # 将后端目录添加到sys.path
            if str(module_path.parent) not in sys.path:
                sys.path.insert(0, str(module_path.parent))
            
            spec.loader.exec_module(module)
            
            # 获取YoloflowBackendModule类
            if hasattr(module, 'YoloflowBackendModule'):
                backend_class = getattr(module, 'YoloflowBackendModule')
                backend_instance = backend_class()
                
                # 更新后端信息
                updated_info = BackendInfo.from_backend(
                    backend_instance, 
                    yoloflow_version,
                    backend_info.module_path
                )
                
                self._backend_infos[backend_name] = updated_info
                self._loaded_backends[backend_name] = backend_instance
                
                # 保存更新的信息到toml文件
                self._save_backend_info_to_toml(backend_name, updated_info)
                
                # 刷新模型选择器
                self.model_selector.refresh_models()
                
                return True
            else:
                print(f"Backend {backend_name} does not have YoloflowBackendModule class")
                return False
                
        except Exception as e:
            print(f"Failed to load backend {backend_name}: {e}")
            return False
    
    def get_backend_instance(self, backend_name: str) -> Optional[BackendBase]:
        """获取已加载的后端实例"""
        return self._loaded_backends.get(backend_name)
    
    def install_backend_dependencies(self, backend_name: str, progress_callback=None) -> bool:
        """安装后端依赖
        
        Args:
            backend_name: 后端名称
            progress_callback: 进度回调函数
            
        Returns:
            bool: 是否安装成功
        """
        backend_info = self._backend_infos.get(backend_name)
        if not backend_info or not backend_info.module_path:
            return False
        
        backend_dir = Path(backend_info.module_path)
        pyproject_file = backend_dir / "pyproject.toml"
        
        if not pyproject_file.exists():
            print(f"No pyproject.toml found in {backend_dir}")
            return False
        
        def install_thread():
            try:
                if progress_callback:
                    progress_callback("初始化虚拟环境...")
                
                # 检查是否已有虚拟环境
                venv_dir = backend_dir / ".venv"
                if not venv_dir.exists():
                    subprocess.run(
                        ["uv", "venv", str(venv_dir)],
                        cwd=backend_dir,
                        check=True,
                        capture_output=True
                    )
                
                if progress_callback:
                    progress_callback("执行前置处理...")
                
                # 如果有后端实例，执行前置处理
                backend_instance = self._loaded_backends.get(backend_name)
                if backend_instance:
                    backend_instance.pre_install(str(backend_dir))
                
                if progress_callback:
                    progress_callback("安装依赖...")
                
                # 安装依赖
                subprocess.run(
                    ["uv", "sync"],
                    cwd=backend_dir,
                    check=True,
                    capture_output=True
                )
                
                if progress_callback:
                    progress_callback("执行后置处理...")
                
                # 执行后置处理
                if backend_instance:
                    backend_instance.post_install(str(backend_dir))
                
                # 更新安装状态
                backend_info.is_installed = True
                self._save_backend_info_to_toml(backend_name, backend_info)
                
                if progress_callback:
                    progress_callback("安装完成")
                
                return True
                
            except subprocess.CalledProcessError as e:
                error_msg = f"命令执行失败: {e}"
                if progress_callback:
                    progress_callback(f"安装失败: {error_msg}")
                print(error_msg)
                return False
            except Exception as e:
                error_msg = f"安装过程中发生错误: {e}"
                if progress_callback:
                    progress_callback(f"安装失败: {error_msg}")
                print(error_msg)
                return False
        
        # 在单独线程中执行安装
        install_thread_obj = Thread(target=install_thread)
        install_thread_obj.start()
        install_thread_obj.join()
        
        return backend_info.is_installed
    
    def uninstall_backend(self, backend_name: str) -> bool:
        """卸载后端
        
        Args:
            backend_name: 后端名称
            
        Returns:
            bool: 是否卸载成功
        """
        try:
            # 从加载的后端中移除
            if backend_name in self._loaded_backends:
                del self._loaded_backends[backend_name]
            
            # 获取后端信息
            backend_info = self._backend_infos.get(backend_name)
            if backend_info and backend_info.module_path:
                backend_dir = Path(backend_info.module_path)
                
                # 删除虚拟环境
                venv_dir = backend_dir / ".venv"
                if venv_dir.exists():
                    shutil.rmtree(venv_dir)
                
                # 更新安装状态
                backend_info.is_installed = False
                self._save_backend_info_to_toml(backend_name, backend_info)
            
            return True
            
        except Exception as e:
            print(f"Failed to uninstall backend {backend_name}: {e}")
            return False
    
    def get_supported_tasks(self) -> Set[TaskType]:
        """获取所有后端支持的任务类型"""
        all_tasks = set()
        for info in self._backend_infos.values():
            if info.is_available and info.is_installed:
                all_tasks.update(info.available_tasks)
        return all_tasks
    
    def get_backends_for_task(self, task_type: TaskType) -> List[BackendInfo]:
        """获取支持指定任务类型的后端"""
        result = []
        for info in self._backend_infos.values():
            if info.is_available and info.is_installed and info.supports_task(task_type):
                result.append(info)
        return result
    
    def get_supported_models(self) -> Set[ModelInfo]:
        """获取所有后端支持的模型 - 内部使用，供ModelSelector调用"""
        all_models = set()
        for info in self._backend_infos.values():
            if info.is_available and info.is_installed:
                all_models.update(info.available_models)
        return all_models
    
    def refresh_backends(self):
        """刷新后端列表"""
        self._backend_infos.clear()
        self._loaded_backends.clear()
        self._scan_backend_directories()
        # 刷新模型选择器
        self.model_selector.refresh_models()