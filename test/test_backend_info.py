"""
BackendInfo 数据类测试
"""

import pytest
from unittest.mock import Mock
from yoloflow.model.backend.backend_info import BackendInfo
from yoloflow.model.enums import BackendUnavailableReason, TaskType
from yoloflow.model.start_up import ModelInfo


def test_backend_info_creation():
    """测试BackendInfo创建"""
    info = BackendInfo(
        name="TestBackend",
        version="1.0.0",
        version_code=1,
        author="Test Author",
        description="Test Description",
        linked_page="https://test.com"
    )
    
    assert info.name == "TestBackend"
    assert info.version == "1.0.0"
    assert info.version_code == 1
    assert info.author == "Test Author"
    assert info.description == "Test Description"
    assert info.linked_page == "https://test.com"


def test_backend_info_from_backend():
    """测试从BackendBase创建BackendInfo"""
    # 创建模拟的BackendBase
    mock_backend = Mock()
    mock_backend.name = "MockBackend"
    mock_backend.version = "2.0.0"
    mock_backend.version_code = 2
    mock_backend.author = "Mock Author"
    mock_backend.description = "Mock Description"
    mock_backend.linked_page = "https://mock.com"
    mock_backend.executable = "mock_cmd"
    mock_backend.extra_params = ["--param1", "--param2"]
    mock_backend.available_tasks = {TaskType.DETECTION}
    mock_backend.available_models = set()
    mock_backend.is_available.return_value = (True, None)

    info = BackendInfo.from_backend(mock_backend)
    assert info.name == "MockBackend"
    assert info.version == "2.0.0"
    assert info.version_code == 2
    assert info.author == "Mock Author"
    assert info.description == "Mock Description"
    assert info.linked_page == "https://mock.com"

if __name__ == "__main__":
    pytest.main([__file__])
