"""
后端管理器测试
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from yoloflow.service.backend_manager import BackendManager
from yoloflow.model.enums import TaskType


def test_backend_manager_initialization():
    """测试后端管理器初始化"""
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = BackendManager(temp_dir)
        assert manager.backends_dir == Path(temp_dir)
        assert manager.backends_dir.exists()


def test_scan_backend_directories():
    """测试扫描后端目录"""
    with tempfile.TemporaryDirectory() as temp_dir:
        backends_dir = Path(temp_dir)
        
        # 创建一个模拟后端目录
        test_backend_dir = backends_dir / "test_backend"
        test_backend_dir.mkdir()
        (test_backend_dir / "__init__.py").touch()
        
        manager = BackendManager(temp_dir)
        
        # 应该发现test_backend
        available_backends = manager.get_available_backends()
        assert "test_backend" in available_backends
        
        # 检查后端信息
        backend_info = manager.get_backend_info("test_backend")
        assert backend_info is not None
        assert backend_info.name == "test_backend"
        assert backend_info.module_path == str(test_backend_dir)


def test_backend_manager_with_real_backend():
    """测试与真实后端的集成"""
    # 使用项目目录下的backends文件夹
    project_root = Path(__file__).parent.parent
    backends_dir = project_root / "backends"
    
    if not backends_dir.exists():
        pytest.skip("backends directory not found")
    
    manager = BackendManager(str(backends_dir))
    
    # 检查是否发现了ultralytics后端
    available_backends = manager.get_available_backends()
    
    if "ultralytics" in available_backends:
        backend_info = manager.get_backend_info("ultralytics")
        assert backend_info is not None
        assert backend_info.name == "Ultralytics YOLO"
        
        # 尝试加载后端
        success = manager.load_backend("ultralytics")
        if success:
            # 检查加载后的信息
            loaded_info = manager.get_backend_info("ultralytics")
            assert loaded_info is not None
            assert loaded_info.name == "Ultralytics YOLO"
            assert TaskType.DETECTION in loaded_info.available_tasks
            
            # 检查后端实例
            instance = manager.get_backend_instance("ultralytics")
            assert instance is not None
            
            # 测试获取支持的任务
            supported_tasks = manager.get_supported_tasks()
            assert len(supported_tasks) > 0
            
            # 测试获取支持的模型
            supported_models = manager.get_supported_models()
            assert len(supported_models) > 0


def test_backend_info_serialization():
    """测试后端信息序列化"""
    with tempfile.TemporaryDirectory() as temp_dir:
        backends_dir = Path(temp_dir)
        
        # 创建模拟后端
        test_backend_dir = backends_dir / "test_backend"
        test_backend_dir.mkdir()
        (test_backend_dir / "__init__.py").write_text("""
class YoloflowBackendModule:
    @property
    def name(self): return "Test Backend"
    @property 
    def version(self): return "1.0.0"
    @property
    def version_code(self): return 100
    @property
    def author(self): return "Test Author"
    @property
    def description(self): return "Test Description"
    @property
    def linked_page(self): return None
    def is_available(self, version): return True, None
    def pre_install(self, dir): pass
    def post_install(self, dir): pass
    @property
    def executable(self): return "test"
    @property
    def extra_params(self): return []
    @property
    def available_tasks(self): return set()
    @property
    def available_models(self): return set()
    def get_download_link(self, model): return None
""")
        
        manager = BackendManager(temp_dir)
        
        # 加载后端
        if manager.load_backend("test_backend"):
            # 检查是否生成了toml文件
            toml_file = backends_dir / "test_backend.toml"
            assert toml_file.exists()
            
            # 重新创建管理器，测试从toml加载
            manager2 = BackendManager(temp_dir)
            backend_info = manager2.get_backend_info("test_backend")
            assert backend_info is not None
            assert backend_info.name == "Test Backend"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
