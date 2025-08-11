"""
工作流栏组件
包含Tab项和运行计划控件
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
                               QComboBox, QLabel, QSizePolicy)
from PySide6.QtCore import Qt, Signal


class WorkflowTab(QPushButton):
    """工作流Tab按钮"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(40)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #bdc3c7;
                border: none;
                font-size: 13px;
                font-weight: bold;
                padding: 0px 20px;
                text-align: left;
            }
            QPushButton:checked {
                background-color: #34495e;
                color: #ecf0f1;
                border-bottom: 2px solid #3498db;
            }
            QPushButton:hover {
                background-color: #34495e;
                color: #ecf0f1;
            }
        """)


class PlanControls(QWidget):
    """运行计划控件"""
    
    plan_selected = Signal(str)  # 计划被选择
    run_clicked = Signal()       # 运行按钮点击
    pause_clicked = Signal()     # 暂停按钮点击
    terminate_clicked = Signal() # 终止按钮点击
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # 计划选择器
        plan_label = QLabel("计划:")
        plan_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 12px;
            }
        """)
        layout.addWidget(plan_label)
        
        self.plan_combo = QComboBox()
        self.plan_combo.setMinimumWidth(150)
        self.plan_combo.setStyleSheet("""
            QComboBox {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #525252;
                border-radius: 3px;
                padding: 3px 8px;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ecf0f1;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #34495e;
                color: #ecf0f1;
                selection-background-color: #3498db;
                border: 1px solid #525252;
            }
        """)
        self.plan_combo.currentTextChanged.connect(self.plan_selected.emit)
        layout.addWidget(self.plan_combo)
        
        # 控制按钮
        button_style = """
            QPushButton {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #525252;
                border-radius: 3px;
                padding: 5px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:disabled {
                background-color: #2c3e50;
                color: #7f8c8d;
            }
        """
        
        # 运行按钮
        self.run_btn = QPushButton("运行")
        self.run_btn.setStyleSheet(button_style + """
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.run_btn.clicked.connect(self.run_clicked.emit)
        layout.addWidget(self.run_btn)
        
        # 暂停按钮
        self.pause_btn = QPushButton("暂停")
        self.pause_btn.setStyleSheet(button_style + """
            QPushButton:hover {
                background-color: #f39c12;
            }
        """)
        self.pause_btn.clicked.connect(self.pause_clicked.emit)
        self.pause_btn.setEnabled(False)
        layout.addWidget(self.pause_btn)
        
        # 终止按钮
        self.terminate_btn = QPushButton("终止")
        self.terminate_btn.setStyleSheet(button_style + """
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        self.terminate_btn.clicked.connect(self.terminate_clicked.emit)
        self.terminate_btn.setEnabled(False)
        layout.addWidget(self.terminate_btn)
    
    def update_plans(self, plans):
        """更新计划列表"""
        self.plan_combo.clear()
        if plans:
            self.plan_combo.addItems(plans)
        else:
            self.plan_combo.addItem("无可用计划")
    
    def set_running_state(self, running):
        """设置运行状态"""
        self.run_btn.setEnabled(not running)
        self.pause_btn.setEnabled(running)
        self.terminate_btn.setEnabled(running)


class WorkflowBar(QWidget):
    """工作流栏"""
    
    # Tab切换信号
    tab_changed = Signal(int)  # 发送Tab索引
    
    # 计划控制信号
    plan_selected = Signal(str)
    run_clicked = Signal()
    pause_clicked = Signal()
    terminate_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tabs = []
        self.current_tab = 0
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        self.setFixedHeight(50)
        self.setStyleSheet("""
            WorkflowBar {
                background-color: #2c3e50;
                border-bottom: 1px solid #34495e;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Tab区域
        tab_widget = QWidget()
        tab_layout = QHBoxLayout(tab_widget)
        tab_layout.setContentsMargins(10, 5, 10, 5)
        tab_layout.setSpacing(0)
        
        # 创建Tab按钮
        tab_names = ["主页", "数据集", "模型", "作业", "训练", "日志", "评估", "导出"]
        for i, name in enumerate(tab_names):
            tab = WorkflowTab(name)
            tab.clicked.connect(lambda checked, idx=i: self._on_tab_clicked(idx))
            self.tabs.append(tab)
            tab_layout.addWidget(tab)
        
        # 设置第一个Tab为选中状态
        if self.tabs:
            self.tabs[0].setChecked(True)
        
        tab_layout.addStretch()
        layout.addWidget(tab_widget, 1)
        
        # 计划控制区域
        self.plan_controls = PlanControls()
        self.plan_controls.plan_selected.connect(self.plan_selected.emit)
        self.plan_controls.run_clicked.connect(self.run_clicked.emit)
        self.plan_controls.pause_clicked.connect(self.pause_clicked.emit)
        self.plan_controls.terminate_clicked.connect(self.terminate_clicked.emit)
        layout.addWidget(self.plan_controls)
    
    def _on_tab_clicked(self, index):
        """Tab点击处理"""
        # 取消其他Tab的选中状态
        for i, tab in enumerate(self.tabs):
            tab.setChecked(i == index)
        
        self.current_tab = index
        self.tab_changed.emit(index)
    
    def set_current_tab(self, index):
        """设置当前Tab"""
        if 0 <= index < len(self.tabs):
            self._on_tab_clicked(index)
    
    def update_plans(self, plans):
        """更新计划列表"""
        self.plan_controls.update_plans(plans)
    
    def set_running_state(self, running):
        """设置运行状态"""
        self.plan_controls.set_running_state(running)
