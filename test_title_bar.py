"""
Test the Project Manager Window with custom title bar.
"""

import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from yoloflow.ui import show_project_manager


if __name__ == "__main__":
    # 显示项目管理器界面
    app, window = show_project_manager()
    sys.exit(app.exec())
