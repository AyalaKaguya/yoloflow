"""
Main entry point for YOLOFlow CLI.
"""

import sys
import argparse
from pathlib import Path
from PySide6.QtWidgets import QApplication
from ..ui import SplashScreen, ProjectManagerWindow, WorkspaceWindow
from ..service import ProjectManager
from ..__version__ import __version__ as version

from typing import Optional


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        prog="yoloflow",
        description="YOLOFlow - YOLO工作流平台",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  yoloflow                           # 启动项目管理器
  yoloflow --project /path/to/proj   # 直接打开指定项目
  yoloflow -p ./my_project           # 直接打开当前目录下的项目
        """
    )
    
    parser.add_argument(
        "--project", "-p",
        type=str,
        help="指定要打开的项目路径"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"YOLOFlow {version}"
    )
    
    return parser.parse_args()


def start_application(target_project_path: Optional[str] = None):
    """统一的应用启动入口"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # 创建启动画面
    splash = SplashScreen()
    splash.show()
    
    # 创建ProjectManager实例
    project_manager = ProjectManager()
    
    # 创建项目管理器窗口（注入ProjectManager）
    project_manager_window = ProjectManagerWindow(project_manager)
    
    def on_splash_finished():
        splash.close()
        try:
            # 如果指定了项目路径，尝试直接打开
            if target_project_path:
                try:
                    # 加载项目
                    project = project_manager.open_project(target_project_path)
                    
                    # 直接创建工作区窗口
                    workspace_window = WorkspaceWindow(project, project_manager)
                    workspace_window.show()
                    
                    # 项目管理器窗口不显示
                    return
                    
                except Exception as e:
                    print(f"打开项目失败: {e}")
                    # 回退到显示项目管理器
            
            # 显示项目管理器
            project_manager_window.show()
            
        except Exception as e:
            print(f"启动失败: {e}")
            sys.exit(1)
    
    # 连接启动画面完成信号
    splash.finished.connect(on_splash_finished)
    
    sys.exit(app.exec())


def main():
    """Main entry point for YOLOFlow application."""
    try:
        args = parse_args()
        start_application(target_project_path=args.project)
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
