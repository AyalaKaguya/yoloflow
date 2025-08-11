"""
状态栏组件
包含文本信息和进度条、页面控制
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QProgressBar, 
                               QPushButton, QSlider)
from PySide6.QtCore import Qt, Signal


class StatusBar(QWidget):
    """状态栏"""
    
    zoom_changed = Signal(int)  # 缩放变化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        self.setFixedHeight(30)
        self.setStyleSheet("""
            StatusBar {
                background-color: #2c3e50;
                border-top: 1px solid #34495e;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # 左侧：状态文本
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # 右侧：进度条和页面控制
        self._create_progress_bars(layout)
        self._create_page_controls(layout)
    
    def _create_progress_bars(self, layout):
        """创建进度条"""
        # 主要进度条
        main_progress_label = QLabel("进度:")
        main_progress_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 11px;
            }
        """)
        layout.addWidget(main_progress_label)
        
        self.main_progress = QProgressBar()
        self.main_progress.setFixedSize(120, 16)
        self.main_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #34495e;
                border-radius: 3px;
                background-color: #34495e;
                text-align: center;
                font-size: 10px;
                color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.main_progress)
        
        # 次要进度条
        sub_progress_label = QLabel("子任务:")
        sub_progress_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 11px;
            }
        """)
        layout.addWidget(sub_progress_label)
        
        self.sub_progress = QProgressBar()
        self.sub_progress.setFixedSize(120, 16)
        self.sub_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #34495e;
                border-radius: 3px;
                background-color: #34495e;
                text-align: center;
                font-size: 10px;
                color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.sub_progress)
    
    def _create_page_controls(self, layout):
        """创建页面控制"""
        # 分隔线
        separator = QWidget()
        separator.setFixedSize(1, 20)
        separator.setStyleSheet("background-color: #34495e;")
        layout.addWidget(separator)
        
        # 缩放控制
        zoom_label = QLabel("缩放:")
        zoom_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 11px;
            }
        """)
        layout.addWidget(zoom_label)
        
        # 缩小按钮
        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setFixedSize(20, 20)
        zoom_out_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #525252;
                border-radius: 3px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        zoom_out_btn.clicked.connect(lambda: self._zoom_change(-10))
        layout.addWidget(zoom_out_btn)
        
        # 缩放滑块
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(25, 200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(80)
        self.zoom_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #34495e;
                height: 4px;
                background: #34495e;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 1px solid #2980b9;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: #5dade2;
            }
        """)
        self.zoom_slider.valueChanged.connect(self.zoom_changed.emit)
        layout.addWidget(self.zoom_slider)
        
        # 放大按钮
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedSize(20, 20)
        zoom_in_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #525252;
                border-radius: 3px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        zoom_in_btn.clicked.connect(lambda: self._zoom_change(10))
        layout.addWidget(zoom_in_btn)
        
        # 缩放百分比显示
        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(35)
        self.zoom_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.zoom_label)
    
    def _zoom_change(self, delta):
        """缩放变化"""
        current = self.zoom_slider.value()
        new_value = max(25, min(200, current + delta))
        self.zoom_slider.setValue(new_value)
    
    def set_status_text(self, text):
        """设置状态文本"""
        self.status_label.setText(text)
    
    def set_main_progress(self, value, maximum=100):
        """设置主进度条"""
        self.main_progress.setMaximum(maximum)
        self.main_progress.setValue(value)
    
    def set_sub_progress(self, value, maximum=100):
        """设置子进度条"""
        self.sub_progress.setMaximum(maximum)
        self.sub_progress.setValue(value)
    
    def set_zoom(self, value):
        """设置缩放值"""
        self.zoom_slider.setValue(value)
        self.zoom_label.setText(f"{value}%")
