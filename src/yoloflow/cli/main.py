"""
Main entry point for YOLOFlow CLI.
"""

import sys
from PySide6.QtWidgets import QApplication
from ..ui import SplashScreen, ProjectManagerWindow


def main():
    """Main entry point for YOLOFlow application."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # 创建启动画面
    splash = SplashScreen()
    splash.show()
    
    # 创建项目管理器窗口（先隐藏）
    project_manager = ProjectManagerWindow()
    
    # 当启动画面完成时，显示项目管理器
    def on_splash_finished():
        splash.close()
        project_manager.show()
    
    # 连接启动画面完成信号到项目管理器显示
    splash.loading_worker.finished.connect(on_splash_finished)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
