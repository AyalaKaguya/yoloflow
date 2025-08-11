"""
数据集页面
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class DatasetPage(QWidget):
    """数据集页面"""
    
    def __init__(self, project, project_manager, parent=None):
        super().__init__(parent)
        self.project = project
        self.project_manager = project_manager
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 临时占位内容
        label = QLabel("数据集页面")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(label)
