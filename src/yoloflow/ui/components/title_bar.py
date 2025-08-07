"""
自定义标题栏组件
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QMouseEvent

from ...__version__ import __version__


class CustomTitleBar(QWidget):
    """自定义标题栏"""
    
    close_clicked = Signal()
    
    def __init__(self, parent=None, title=None):
        super().__init__(parent)
        self.parent_window = parent
        self.dragging = False
        self.drag_position = QPoint()
        self.title = title or f"YOLOFlow v{__version__}"
        self._setup_ui()
    
    def _setup_ui(self):
        """设置标题栏UI"""
        self.setFixedHeight(40)
        self.setStyleSheet("""
            CustomTitleBar {
                background-color: #2c3e50;
                border-bottom: 1px solid #34495e;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 10, 0)
        layout.setSpacing(10)
        
        # 应用名称和版本号
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        # 弹性空间
        layout.addStretch()
        
        # 关闭按钮
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(40, 30)  # 4:3比例
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #bdc3c7;
                border: none;
                font-size: 18px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
        """)
        self.close_btn.clicked.connect(self.close_clicked.emit)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.close_btn)
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件 - 开始拖拽"""
        if event.button() == Qt.LeftButton and self.parent_window:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件 - 拖拽窗口"""
        if event.buttons() == Qt.LeftButton and self.dragging and self.parent_window:
            self.parent_window.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件 - 结束拖拽"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
