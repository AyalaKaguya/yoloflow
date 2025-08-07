"""
Test the Project Manager Window.
"""

import sys
import tempfile
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from yoloflow.ui import show_project_manager
from yoloflow.service.project_manager import ProjectManager
from yoloflow.model import TaskType


def create_sample_projects():
    """创建一些示例项目用于测试"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 使用临时数据库
        manager = ProjectManager(str(temp_path / "test.db"))
        
        # 创建几个示例项目
        for i in range(3):
            project_path = temp_path / f"sample_project_{i}"
            manager.create_project(
                str(project_path),
                f"示例项目 {i+1}",
                TaskType.DETECTION,
                f"这是第{i+1}个示例项目"
            )
        
        manager.close()
        print(f"创建了3个示例项目在: {temp_path}")
        return str(temp_path / "test.db")


if __name__ == "__main__":
    # 可选：创建示例数据用于测试
    # create_sample_projects()
    
    # 显示项目管理器界面
    app, window = show_project_manager()
    sys.exit(app.exec())
