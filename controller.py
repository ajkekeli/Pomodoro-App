"""
Pomodoro Timer - Controller
Coordinates between Model and View, handles user interactions
"""
import tkinter as tk
from model import PomodoroModel
from view import PomodoroView
from history import HistoryWindow
  
class PomodoroController:
    """
    Controller class for Pomodoro timer application.
    Manages communication between Model and View.
    """
    
    def __init__(self, root: tk.Tk):
        """Initialize controller with root window."""
        self.root = root
    
        # Initialize Model and View
        self.model = PomodoroModel()
        self.view = PomodoroView(root)
        
        # Connect view callbacks to controller methods
        self.view.on_start_stop = self.handle_start_stop
        self.view.on_pause = self.handle_pause
        self.view.on_reset = self.handle_reset
        self.view.on_settings = self.handle_settings
        self.view.on_history = self.handle_history
        
        # Register controller as observer of model
        self.model.add_observer(self.update_view)
        
        # Timer reference
        self.timer_job = None
        
        # Sound notification flag
        self.notification_shown = False
        
        # Initial view update
        self.update_view()
    
    def handle_start_stop(self):
        """Handle start/stop button press."""
        current_state = self.model.session_state['state']
        
        if current_state == PomodoroModel.STATE_IDLE or current_state == PomodoroModel.STATE_PAUSED:
            # Start or resume the timer
            self.model.start_timer()
            self._start_tick()
            self.notification_shown = False
        elif current_state == PomodoroModel.STATE_RUNNING:
            # Stop the timer completely
            self.model.stop_timer()
            self._stop_tick()
    
    def handle_pause(self):
        """Handle pause button press."""
        current_state = self.model.session_state['state']
        
        if current_state == PomodoroModel.STATE_RUNNING:
            # Pause the timer
            self.model.pause_timer()
            self._stop_tick()
    
    def handle_reset(self):
        """Handle reset button press."""
        self._stop_tick()
        self.model.reset_all()
        self.notification_shown = False
    
    def handle_history(self):
        """Handle history button press."""
        was_running = self.model.session_state['state'] == PomodoroModel.STATE_RUNNING
        if was_running:
            self.model.pause_timer()
        self._stop_tick()
    
        statistics = self.model.statistics.copy()
        HistoryWindow(self.root, statistics)
    
        if was_running:
            self.model.start_timer()
        self._start_tick()
        
    # Show history window
        statistics = self.model.statistics.copy()
        HistoryWindow(self.root, statistics)
    
    # Resume timer if it was running
        if was_running:
            self.model.start_timer()
            self._start_tick()
    
    def handle_settings(self):
        """Handle settings button press."""
        # Pause timer if running
        was_running = self.model.session_state['state'] == PomodoroModel.STATE_RUNNING
        if was_running:
            self.model.pause_timer()
            self._stop_tick()
        
        # Show settings dialog
        current_config = self.model.config.copy()
        new_config = self.view.show_settings_dialog(current_config)
        
        # Apply new settings if saved
        if new_config:
            self.model.update_config(new_config)
        
        # Resume timer if it was running
        if was_running:
            self.model.start_timer()
            self._start_tick()
    
    def _start_tick(self):
        """Start the timer tick."""
        self._tick()
    
    def _stop_tick(self):
        """Stop the timer tick."""
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
    
    def _tick(self):
        """Timer tick - called every second."""
        session_complete = self.model.tick()
        
        if session_complete:
            self._handle_session_complete()
        
        # Schedule next tick if timer is still running
        if self.model.session_state['state'] == PomodoroModel.STATE_RUNNING:
            self.timer_job = self.root.after(1000, self._tick)
        else:
            self.timer_job = None
    
    def _handle_session_complete(self):
        """Handle completion of a session."""
        session_type = self.model.session_state['session_type']
        
        # Show notification
        if not self.notification_shown:
            if session_type == PomodoroModel.SESSION_WORK:
                self.view.show_notification(
                    "Break Complete!",
                    "Ready to get back to work?"
                )
            else:
                self.view.show_notification(
                   "Break Time!",
                    "Great work! Time for a break."
                )
            self.notification_shown = True
        
        # Play sound
        self._play_notification_sound()
        
        # Check if auto-start is enabled
        if self.model.session_state['state'] == PomodoroModel.STATE_RUNNING:
            # Auto-start is enabled, continue ticking
            self._tick()
        else:
            # Stop ticking, wait for user to start
            self._stop_tick()
    
    def _play_notification_sound(self):
        """Play notification sound."""
        try:
            # Try to use winsound on Windows
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except (ImportError, RuntimeError):
            # Fallback to system bell
            try:
                self.root.bell()
            except:
                pass

    def update_view(self):
        """Update view with current model state."""
        state = self.model.get_state_dict()
        self.view.update_display(state)
    
    def run(self):
        """Start the application main loop."""
        self.root.mainloop()
    
    def cleanup(self):
        """Cleanup before closing."""
        self._stop_tick()
        # Save any pending statistics
        self.model._save_statistics()