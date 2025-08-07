"""
Create sample projects for testing the UI.
"""

import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from yoloflow.service.project_manager import ProjectManager
from yoloflow.model import TaskType


def create_sample_projects():
    """创建一些示例项目用于测试"""
    # 在当前工作目录创建示例项目
    base_path = Path.cwd() / "sample_projects"
    base_path.mkdir(exist_ok=True)
    
    manager = ProjectManager()  # 使用默认数据库路径
    
    # 创建几个示例项目
    projects = [
        ("YOLO目标检测项目", TaskType.DETECTION, "用于车辆检测的YOLO项目"),
        ("图像分类项目", TaskType.CLASSIFICATION, "猫狗分类项目"),
        ("语义分割项目", TaskType.SEGMENTATION, "道路分割项目"),
    ]
    
    for i, (name, task_type, description) in enumerate(projects):
        project_path = base_path / f"project_{i+1}_{task_type.value}"
        try:
            project = manager.create_project(
                str(project_path),
                name,
                task_type,
                description
            )
            print(f"✅ 创建项目: {name} -> {project_path}")
        except Exception as e:
            print(f"❌ 创建项目失败 {name}: {e}")
    
    manager.close()
    print(f"\n示例项目已创建在: {base_path}")
    print("现在可以运行项目管理器界面测试了")


if __name__ == "__main__":
    create_sample_projects()
