"""
UI工具函数，提供统一的深色主题MessageBox
"""

from PySide6.QtWidgets import QMessageBox, QWidget
from typing import Optional


def show_warning_message(parent: Optional[QWidget], title: str, message: str) -> None:
    """显示样式化的警告对话框"""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    
    # 设置深色主题样式
    msg_box.setStyleSheet("""
        QMessageBox {
            background-color: #2b2b2b;
            color: white;
            border: 1px solid #666;
        }
        QMessageBox QLabel {
            color: white;
            font-size: 12px;
        }
        QMessageBox QPushButton {
            background-color: #007ACC;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            min-width: 80px;
        }
        QMessageBox QPushButton:hover {
            background-color: #005999;
        }
        QMessageBox QPushButton:pressed {
            background-color: #004477;
        }
    """)
    
    msg_box.exec()


def show_critical_message(parent: Optional[QWidget], title: str, message: str) -> None:
    """显示样式化的错误对话框"""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    
    # 设置深色主题样式（错误用红色强调）
    msg_box.setStyleSheet("""
        QMessageBox {
            background-color: #2b2b2b;
            color: white;
            border: 1px solid #666;
        }
        QMessageBox QLabel {
            color: white;
            font-size: 12px;
        }
        QMessageBox QPushButton {
            background-color: #dc3545;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            min-width: 80px;
        }
        QMessageBox QPushButton:hover {
            background-color: #c82333;
        }
        QMessageBox QPushButton:pressed {
            background-color: #bd2130;
        }
    """)
    
    msg_box.exec()


def show_information_message(parent: Optional[QWidget], title: str, message: str) -> None:
    """显示样式化的信息对话框"""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    
    # 设置深色主题样式（信息用绿色强调）
    msg_box.setStyleSheet("""
        QMessageBox {
            background-color: #2b2b2b;
            color: white;
            border: 1px solid #666;
        }
        QMessageBox QLabel {
            color: white;
            font-size: 12px;
        }
        QMessageBox QPushButton {
            background-color: #28a745;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            min-width: 80px;
        }
        QMessageBox QPushButton:hover {
            background-color: #218838;
        }
        QMessageBox QPushButton:pressed {
            background-color: #1e7e34;
        }
    """)
    
    msg_box.exec()
