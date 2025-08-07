"""
Main entry point for YOLOFlow CLI.
"""

import sys
from ..ui import show_splash_screen


def main():
    """Main entry point for YOLOFlow application."""
    app, splash = show_splash_screen()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
