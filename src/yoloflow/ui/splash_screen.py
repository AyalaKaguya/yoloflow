"""
Splash Screen for YOLOFlow application.
Displays loading information while initializing heavy libraries like PyTorch.
"""

import sys
import time
from pathlib import Path
from PySide6.QtWidgets import QApplication, QSplashScreen, QLabel
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QPixmap, QPainter, QFont, QColor
from ..__version__ import __version__


class LoadingWorker(QThread):
    """Worker thread for loading heavy libraries in background."""
    
    progress = Signal(str)  # Signal to update loading message
    finished = Signal()     # Signal when loading is complete
    
    def run(self):
        """Load heavy libraries and emit progress updates."""
        loading_steps = [
            ("初始化应用程序...", 0.2),
            ("加载OpenCV库...", 0.5),
            ("预加载PyTorch组件...", 0.8),
            ("初始化完成", 0.1),
        ]
        
        for message, delay in loading_steps:
            self.progress.emit(message)
            time.sleep(delay)
        
        self.finished.emit()


class SplashScreen(QSplashScreen):
    """Custom splash screen with loading progress display."""
    
    finished = Signal()  # 添加完成信号
    
    def __init__(self):
        # Create a simple colored pixmap as placeholder
        pixmap = self._create_placeholder_image()
        super().__init__(pixmap, Qt.WindowType.WindowStaysOnTopHint)

        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)

        # Setup UI elements
        self._setup_ui()
        
        # Track timing and prevent double emission
        self.start_time = time.time()
        self.min_display_time = 2.0  # Minimum 2 seconds display
        self._finished_emitted = False  # 防止重复发射信号
        
        # Setup loading worker
        self.loading_worker = LoadingWorker()
        self.loading_worker.progress.connect(self._update_message)
        self.loading_worker.finished.connect(self._on_loading_finished)
        
        # Start loading
        self.loading_worker.start()
    
    def _create_placeholder_image(self):
        """Create a simple placeholder image for the splash screen."""
        width, height = 600, 400
        pixmap = QPixmap(width, height)
        
        # Fill with a gradient-like color
        pixmap.fill(QColor(45, 52, 64))  # Dark blue-gray background
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw title
        painter.setPen(QColor(255, 255, 255))
        title_font = QFont("Arial", 36, QFont.Weight.Bold)
        painter.setFont(title_font)
        painter.drawText(50, 150, "YOLOFlow")
        
        # Draw subtitle
        subtitle_font = QFont("Arial", 14)
        painter.setFont(subtitle_font)
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(50, 180, "YOLO工作流平台")
        
        painter.end()
        return pixmap
    
    def _setup_ui(self):
        """Setup UI elements for the splash screen."""
        # Message label (bottom left)
        self.message_label = QLabel(self)
        self.message_label.setStyleSheet("""
            QLabel {
                color: white;
                padding: 8px 12px;
                font-size: 12px;
                border: none;
                background: transparent;
            }
        """)
        self.message_label.setText("正在启动...")
        self.message_label.adjustSize()
        
        # Version label (bottom right)
        self.version_label = QLabel(self)
        self.version_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 10px;
            }
        """)
        self.version_label.setText(f"v{__version__}")
        self.version_label.adjustSize()
        
        # Position labels
        self._position_labels()
    
    def _position_labels(self):
        """Position the labels on the splash screen."""
        splash_rect = self.rect()
        
        # Message label at bottom left
        self.message_label.move(
            20, 
            splash_rect.height() - self.message_label.height() - 20
        )
        
        # Version label at bottom right
        self.version_label.move(
            splash_rect.width() - self.version_label.width() - 20,
            splash_rect.height() - self.version_label.height() - 20
        )
    
    def _update_message(self, message):
        """Update the loading message."""
        self.message_label.setText(message)
        self.message_label.adjustSize()
        self._position_labels()  # Reposition after resize
        
        # Force repaint
        self.repaint()
    
    def _on_loading_finished(self):
        """Handle when loading is complete."""
        elapsed_time = time.time() - self.start_time
        
        if elapsed_time < self.min_display_time:
            # Wait until minimum display time is reached
            remaining_time = int((self.min_display_time - elapsed_time) * 1000)
            QTimer.singleShot(remaining_time, self._close_splash)
        else:
            self._close_splash()
    
    def _close_splash(self):
        """Close the splash screen and signal completion."""
        if not self._finished_emitted:
            self._finished_emitted = True
            self.finished.emit()  # 发射完成信号
        self.close()


def show_splash_screen():
    """Show the splash screen and handle the application lifecycle."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    splash = SplashScreen()
    splash.show()
    
    return app, splash


if __name__ == "__main__":
    app, splash = show_splash_screen()
    sys.exit(app.exec())
