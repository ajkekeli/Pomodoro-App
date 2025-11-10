"""
Pomodoro Timer Application - MAIN ENTRY POINT WITH SPLASH
"""

import tkinter as tk
from controller import PomodoroController


def main():
    """Main entry point with splash screen."""
    
    # CREATE MAIN APPLICATION FIRST
    root = tk.Tk()
    
    # Set window icon
    try:
        root.iconbitmap('assets/imgs/icon.ico')
    except:
        pass
    
    # Initialize controller
    controller = PomodoroController(root)
    
    # Handle window close
    def on_closing():
        controller.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start application
    controller.run()


if __name__ == "__main__":
    main()