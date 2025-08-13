"""
Main entry point for YOLOFlow CLI.
"""

import sys
import argparse
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from ..ui import SplashScreen, ProjectManagerWindow, WorkspaceWindow
from ..service import ProjectManager
from ..__version__ import __version__ as version

from typing import Optional


def show_error_dialog(parent, title: str, message: str, details: Optional[str] = None):
    """显示错误对话框"""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    
    if details:
        msg_box.setDetailedText(f"详细错误信息:\n{details}")
    
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.setMinimumWidth(400)  # 设置对话框最小宽度
    msg_box.exec()


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
                    
                except FileNotFoundError as e:
                    show_error_dialog(
                        None,
                        "项目不存在",
                        f"指定的项目不存在或已被移动：\n{target_project_path}",
                        f"请检查项目路径是否正确，或在项目管理器中重新选择项目"
                    )
                    # 回退到显示项目管理器
                except ValueError as e:
                    show_error_dialog(
                        None,
                        "无效的项目",
                        f"指定的目录不是有效的YOLOFlow项目：\n{target_project_path}",
                        f"错误详情：{str(e)}\n\n请确认目录中包含正确的yoloflow.toml配置文件"
                    )
                    # 回退到显示项目管理器
                except PermissionError as e:
                    show_error_dialog(
                        None,
                        "权限不足",
                        f"没有权限访问项目目录：\n{target_project_path}",
                        f"请检查目录权限或以管理员身份运行程序"
                    )
                    # 回退到显示项目管理器
                except Exception as e:
                    show_error_dialog(
                        None,
                        "打开项目失败",
                        f"无法打开项目：\n{target_project_path}",
                        f"未知错误：{str(e)}\n\n请检查项目文件是否完整或联系技术支持"
                    )
                    # 回退到显示项目管理器
            
            # 显示项目管理器
            project_manager_window.show()
            
        except Exception as e:
            show_error_dialog(
                None,
                "应用启动失败",
                "YOLOFlow启动时发生错误",
                f"错误详情：{str(e)}"
            )
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
