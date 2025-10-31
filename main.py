
import tkinter as tk
from controller import PomodoroController


def main():
    """
    Main entry point for the Pomodoro Timer application.
    Creates the root window and initializes the controller.
    """
    # Create root window
    root = tk.Tk()
    
    # Set window icon 
    try:
        root.iconbitmap('Icon.ico')
    except:
        pass  # Icon file not found, continue without it
    
    # Initialize controller (which creates model and view)
    controller = PomodoroController(root)
    
    # Handle window close event
    def on_closing():
        """Clean up and close the application."""
        controller.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the application
    controller.run()


if __name__ == "__main__":
    main()
