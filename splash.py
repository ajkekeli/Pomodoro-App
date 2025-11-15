"""
Splash Screen with GIF Animation for Pomodoro Timer
"""

import tkinter as tk
from PIL import Image, ImageTk, ImageSequence


class SplashScreen:
    """Splash screen with animated GIF playback."""

    def __init__(self, gif_path: str, duration: int = 5000, bg_color="#2C3E50"):
        """
        Initialize splash screen.

        Args:
            gif_path: Path to GIF file
            duration: Duration in milliseconds (default 5 seconds)
            bg_color: Background color
        """
        self.gif_path = gif_path
        self.duration = duration
        self.bg_color = bg_color
        self.root = None
        self.label = None
        self.frames = []
        self.is_playing = True

    def show(self, parent=None):
        """Display the splash screen."""
        # Create splash window
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
            self.root.withdraw()

        # Load frames from GIF
        self._load_gif()

        if not self.frames:
            self._show_fallback()
            return

        # Window setup
        width, height = self.frames[0].width(), self.frames[0].height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.overrideredirect(True)
        self.root.configure(bg=self.bg_color)
        self.root.attributes('-topmost', True)

        # GIF label
        self.label = tk.Label(self.root, bg=self.bg_color)
        self.label.pack(expand=True)

        # Show window
        if not parent:
            self.root.deiconify()

        # Start animation
        self._animate(0)

        # Close splash after duration
        self.root.after(self.duration, self._close)

        # Wait until closed
        self.root.wait_window()

    def _load_gif(self):
        """This method loads all frames from the GIF."""
        try:
            gif = Image.open(self.gif_path)
            for frame in ImageSequence.Iterator(gif):
                frame_image = ImageTk.PhotoImage(frame.copy())
                self.frames.append(frame_image)
        except Exception as e:
            print(f"Error loading GIF: {e}")
            self.frames = []

    def _animate(self, index):
        """This method animates GIF frames recursively."""
        if not self.is_playing or not self.frames:
            return

        frame = self.frames[index]
        self.label.config(image=frame)
        self.label.image = frame  # Keep reference

        next_index = (index + 1) % len(self.frames)
        self.root.after(80, self._animate, next_index)  # Adjust speed here

    def _show_fallback(self):
        """Show fallback text if GIF fails."""
        self.root.overrideredirect(True)
        self.root.configure(bg=self.bg_color)
        self.root.attributes('-topmost', True)

        self.label = tk.Label(
            self.root,
            text="🍅 Pomodoro Timer\n\nLoading...",
            font=("Helvetica", 28, "bold"),
            fg="white",
            bg=self.bg_color
        )
        self.label.pack(expand=True, fill="both")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width, height = 500, 300
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.root.after(self.duration, self._close)
        self.root.deiconify()
        self.root.mainloop()

    def _close(self):
        """Close splash screen."""
        self.is_playing = False
        if self.root:
            self.root.destroy()


def show_splash(gif_path: str, duration: int = 5000):
    """
    Show splash screen with GIF animation.

    Args:
        gif_path: Path to GIF file
        duration: Duration in milliseconds
    """
    splash = SplashScreen(gif_path, duration)
    splash.show()
