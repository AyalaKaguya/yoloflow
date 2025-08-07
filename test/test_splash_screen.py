"""
Test splash screen functionality.
"""

import pytest
from yoloflow.ui.splash_screen import LoadingWorker


class TestLoadingWorker:
    """Test the LoadingWorker thread."""
    
    def test_loading_worker_signals(self):
        """Test that LoadingWorker emits progress and finished signals."""
        worker = LoadingWorker()
        
        # Mock the signals
        progress_messages = []
        finished_called = False
        
        def on_progress(message):
            progress_messages.append(message)
        
        def on_finished():
            nonlocal finished_called
            finished_called = True
        
        worker.progress.connect(on_progress)
        worker.finished.connect(on_finished)
        
        # Run worker (this will take some time due to sleep calls)
        worker.run()
        
        # Check that progress messages were emitted
        assert len(progress_messages) == 4
        assert "初始化应用程序..." in progress_messages
        assert "加载OpenCV库..." in progress_messages
        assert "预加载PyTorch组件..." in progress_messages
        assert "初始化完成" in progress_messages
        
        # Check that finished signal was emitted
        assert finished_called


if __name__ == "__main__":
    pytest.main([__file__])
