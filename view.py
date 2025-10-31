"""
Pomodoro Timer - View
Handles all UI components and rendering
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
from typing import Dict, Callable


class PomodoroView:
    """
    View class for Pomodoro timer application.
    Manages all UI elements and user interactions.
    """
    
    # Color schemes
    WORK_COLORS = {
        'primary': '#4A90E2',
        'secondary': '#357ABD',
        'bg': '#F0F4F8',
        'text': '#2C3E50',
        'progress': '#4A90E2',
        'progress_bg': '#D6E4F0',
    }
    
    BREAK_COLORS = {
        'primary': '#27AE60',
        'secondary': '#1E8449',
        'bg': '#E8F8F5',
        'text': '#145A32',
        'progress': '#27AE60',
        'progress_bg': '#D5F4E6',
    }
    
    def __init__(self, root: tk.Tk):
        """Initialize the view with the root window."""
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("500x700")
        self.root.resizable(True, True)
        
        # Current color scheme
        self.current_colors = self.WORK_COLORS
        
        # Controller callbacks (to be set by controller)
        self.on_start_stop: Callable = None
        self.on_pause: Callable = None
        self.on_reset: Callable = None
        self.on_settings: Callable = None
        
        # Create UI components
        self._create_widgets()
        self._apply_theme(self.WORK_COLORS)
    
    def _create_widgets(self):
        """Create all UI widgets."""
        # Main container
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Top section - Cycle indicator
        self._create_cycle_section()
        
        # Middle section - Timer circle
        self._create_timer_section()
        
        # Lower section - Progress indicators
        self._create_progress_section()
        
        # Bottom section - Control buttons
        self._create_control_section()
        
        # Settings button (top right corner)
        self._create_settings_button()
    
    def _create_cycle_section(self):
        """Create cycle indicator at the top."""
        cycle_frame = tk.Frame(self.main_frame, bg=self.current_colors['bg'])
        cycle_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.cycle_label = tk.Label(
            cycle_frame,
            text="CYCLE 1/4",
            font=('Helvetica', 14, 'bold'),
            bg=self.current_colors['bg'],
            fg=self.current_colors['text']
        )
        self.cycle_label.pack()
    
    def _create_timer_section(self):
        """Create the main circular timer display."""
        timer_frame = tk.Frame(self.main_frame, bg=self.current_colors['bg'])
        timer_frame.pack(pady=20)
        
        # Canvas for circular progress
        self.canvas = tk.Canvas(
            timer_frame,
            width=300,
            height=300,
            bg=self.current_colors['bg'],
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Draw progress circle background
        self.progress_bg_arc = self.canvas.create_arc(
            20, 20, 280, 280,
            start=90,
            extent=359.99,
            outline=self.current_colors['progress_bg'],
            width=15,
            style=tk.ARC
        )
        
        # Draw progress circle
        self.progress_arc = self.canvas.create_arc(
            20, 20, 280, 280,
            start=90,
            extent=0,
            outline=self.current_colors['progress'],
            width=15,
            style=tk.ARC
        )
        
        # Session type label
        self.session_label = tk.Label(
            self.canvas,
            text="Work Session",
            font=('Helvetica', 16, 'bold'),
            bg=self.current_colors['bg'],
            fg=self.current_colors['primary']
        )
        self.canvas.create_window(150, 110, window=self.session_label)
        
        # Time label
        self.time_label = tk.Label(
            self.canvas,
            text="25:00",
            font=('Helvetica', 48, 'bold'),
            bg=self.current_colors['bg'],
            fg=self.current_colors['text']
        )
        self.canvas.create_window(150, 170, window=self.time_label)
    
    def _create_progress_section(self):
        """Create progress indicators section."""
        progress_frame = tk.Frame(self.main_frame, bg=self.current_colors['bg'])
        progress_frame.pack(pady=20, fill=tk.X)
        
        # Work sessions indicator
        work_frame = tk.Frame(progress_frame, bg=self.current_colors['bg'])
        work_frame.pack(side=tk.LEFT, expand=True, padx=10)
        
        tk.Label(
            work_frame,
            text="Work Sessions",
            font=('Helvetica', 10),
            bg=self.current_colors['bg'],
            fg=self.current_colors['text']
        ).pack()
        
        self.work_progress = tk.Label(
            work_frame,
            text="0",
            font=('Helvetica', 24, 'bold'),
            bg=self.current_colors['bg'],
            fg=self.WORK_COLORS['primary']
        )
        self.work_progress.pack()
        
        # Break sessions indicator
        break_frame = tk.Frame(progress_frame, bg=self.current_colors['bg'])
        break_frame.pack(side=tk.LEFT, expand=True, padx=10)
        
        tk.Label(
            break_frame,
            text="Breaks",
            font=('Helvetica', 10),
            bg=self.current_colors['bg'],
            fg=self.current_colors['text']
        ).pack()
        
        self.break_progress = tk.Label(
            break_frame,
            text="0",
            font=('Helvetica', 24, 'bold'),
            bg=self.current_colors['bg'],
            fg=self.BREAK_COLORS['primary']
        )
        self.break_progress.pack()
        
        # Mini graph section
        self._create_mini_graph(progress_frame)
    
    def _create_mini_graph(self, parent):
        """Create a mini graph showing session distribution."""
        graph_frame = tk.Frame(parent, bg=self.current_colors['bg'])
        graph_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(
            graph_frame,
            text="Today's Progress",
            font=('Helvetica', 10),
            bg=self.current_colors['bg'],
            fg=self.current_colors['text']
        ).pack()
        
        # Canvas for mini bar graph
        self.graph_canvas = tk.Canvas(
            graph_frame,
            width=400,
            height=60,
            bg=self.current_colors['bg'],
            highlightthickness=0
        )
        self.graph_canvas.pack(pady=5)
    
    def _create_control_section(self):
        """Create control buttons section."""
        control_frame = tk.Frame(self.main_frame, bg=self.current_colors['bg'])
        control_frame.pack(pady=20)
        
        # Start/Stop button
        self.start_stop_btn = tk.Button(
            control_frame,
            text="START",
            font=('Helvetica', 16, 'bold'),
            bg=self.current_colors['primary'],
            fg='white',
            activebackground=self.current_colors['secondary'],
            activeforeground='white',
            relief=tk.FLAT,
            padx=60,
            pady=15,
            cursor='hand2',
            command=self._handle_start_stop
        )
        self.start_stop_btn.pack(pady=5)
        
        
        
        # Reset button (smaller, secondary)
        self.reset_btn = tk.Button(
            control_frame,
            text="Reset",
            font=('Helvetica', 10),
            bg=self.current_colors['bg'],
            fg=self.current_colors['text'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self._handle_reset
        )
        self.reset_btn.pack(pady=5)
    
    def _create_settings_button(self):
        """Create settings button in top right."""
        settings_btn = tk.Button(
            self.main_frame,
            text="⚙",
            font=('Helvetica', 16),
            bg=self.current_colors['bg'],
            fg=self.current_colors['text'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self._handle_settings
        )
        settings_btn.place(relx=1.0, rely=0.0, anchor='ne')
    
    def _handle_start_stop(self):
        """Handle start/stop button click."""
        if self.on_start_stop:
            self.on_start_stop()
    
    def _handle_reset(self):
        """Handle reset button click."""
        if self.on_reset:
            if messagebox.askyesno("Reset", "Reset all progress and cycles?"):
                self.on_reset()
    
    def _handle_settings(self):
        """Handle settings button click."""
        if self.on_settings:
            self.on_settings()
    
    def update_display(self, state: Dict):
        """Update all display elements based on state."""
        session = state['session']
        statistics = state['statistics']
        
        # Update cycle label
        self.cycle_label.config(
            text=f"CYCLE {session['current_cycle']}/{session['total_cycles']}"
        )
        
        # Update time label
        minutes = session['current_time'] // 60
        seconds = session['current_time'] % 60
        self.time_label.config(text=f"{minutes:02d}:{seconds:02d}")
        
        # Update session label
        session_type = session['session_type']
        if session_type == 'work':
            self.session_label.config(text="Work Session")
        elif session_type == 'short_break':
            self.session_label.config(text="Short Break")
        else:
            self.session_label.config(text="Long Break")
        
        # Update progress counters
        self.work_progress.config(text=str(session['completed_work_sessions']))
        self.break_progress.config(text=str(session['completed_break_sessions']))
        
        # Update start/stop button
        if session['state'] == 'running':
            self.start_stop_btn.config(
                text="STOP",
                bg='#E74C3C'
            )
        else:
            self.start_stop_btn.config(
                text="START",
                bg=self.current_colors['primary']
            )
        
        # Update color theme based on session type
        if session_type == 'work':
            if self.current_colors != self.WORK_COLORS:
                self._apply_theme(self.WORK_COLORS)
        else:
            if self.current_colors != self.BREAK_COLORS:
                self._apply_theme(self.BREAK_COLORS)
        
        # Update progress arc
        self._update_progress_arc(state)
        
        # Update mini graph
        self._update_mini_graph(statistics['today_sessions'])
    
    def _update_progress_arc(self, state: Dict):
        """Update the circular progress indicator."""
        session = state['session']
        session_type = session['session_type']
        current_time = session['current_time']
        
        # Get total time for current session
        if session_type == 'work':
            total_time = state['config']['work_duration']
        elif session_type == 'short_break':
            total_time = state['config']['short_break_duration']
        else:
            total_time = state['config']['long_break_duration']
        
        # Calculate progress
        progress = ((total_time - current_time) / total_time) * 100 if total_time > 0 else 0
        extent = -359.99 * (progress / 100)
        
        # Update arc
        self.canvas.itemconfig(self.progress_arc, extent=extent)
    
    def _update_mini_graph(self, sessions: list):
        """Update the mini bar graph."""
        self.graph_canvas.delete('all')
        
        if not sessions:
            return
        
        # Show last 10 sessions
        recent_sessions = sessions[-10:]
        bar_width = 35
        bar_spacing = 5
        max_height = 50
        
        for i, session in enumerate(recent_sessions):
            x = i * (bar_width + bar_spacing) + 10
            # Normalize height based on duration
            height = (session['duration'] / 1500) * max_height  # 1500s = 25min
            height = min(height, max_height)
            
            color = self.WORK_COLORS['primary'] if session['type'] == 'work' else self.BREAK_COLORS['primary']
            
            self.graph_canvas.create_rectangle(
                x, max_height - height + 5,
                x + bar_width, max_height + 5,
                fill=color,
                outline=''
            )
    
    def _apply_theme(self, colors: Dict):
        """Apply color theme to all UI elements."""
        self.current_colors = colors
        
        # Update background colors
        self.root.configure(bg=colors['bg'])
        self.main_frame.configure(bg=colors['bg'])
        
        # Update labels
        self.cycle_label.configure(bg=colors['bg'], fg=colors['text'])
        
        # Update canvas
        self.canvas.configure(bg=colors['bg'])
        self.session_label.configure(bg=colors['bg'], fg=colors['primary'])
        self.time_label.configure(bg=colors['bg'], fg=colors['text'])
        
        # Update progress arcs
        self.canvas.itemconfig(self.progress_bg_arc, outline=colors['progress_bg'])
        self.canvas.itemconfig(self.progress_arc, outline=colors['progress'])
        
        # Update graph canvas
        self.graph_canvas.configure(bg=colors['bg'])
    
    def show_notification(self, title: str, message: str):
        """Show a notification dialog."""
        messagebox.showinfo(title, message)
    
    def show_settings_dialog(self, current_config: Dict) -> Dict:
        """Show settings dialog and return updated config."""
        dialog = SettingsDialog(self.root, current_config)
        self.root.wait_window(dialog.dialog)
        return dialog.result


class SettingsDialog:
    """Dialog for configuring Pomodoro settings."""
    
    def __init__(self, parent, current_config: Dict):
        """Initialize settings dialog."""
        self.result = None
        self.current_config = current_config
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("400x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dialog widgets."""
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Work duration
        tk.Label(main_frame, text="Work Duration (minutes):", font=('Helvetica', 10)).grid(
            row=0, column=0, sticky='w', pady=10
        )
        self.work_duration = tk.Spinbox(
            main_frame, from_=1, to=60, width=10,
            font=('Helvetica', 10)
        )
        self.work_duration.delete(0, tk.END)
        self.work_duration.insert(0, str(self.current_config['work_duration'] // 60))
        self.work_duration.grid(row=0, column=1, pady=10)
        
        # Short break duration
        tk.Label(main_frame, text="Short Break (minutes):", font=('Helvetica', 10)).grid(
            row=1, column=0, sticky='w', pady=10
        )
        self.short_break = tk.Spinbox(
            main_frame, from_=1, to=30, width=10,
            font=('Helvetica', 10)
        )
        self.short_break.delete(0, tk.END)
        self.short_break.insert(0, str(self.current_config['short_break_duration'] // 60))
        self.short_break.grid(row=1, column=1, pady=10)
        
        # Long break duration
        tk.Label(main_frame, text="Long Break (minutes):", font=('Helvetica', 10)).grid(
            row=2, column=0, sticky='w', pady=10
        )
        self.long_break = tk.Spinbox(
            main_frame, from_=1, to=60, width=10,
            font=('Helvetica', 10)
        )
        self.long_break.delete(0, tk.END)
        self.long_break.insert(0, str(self.current_config['long_break_duration'] // 60))
        self.long_break.grid(row=2, column=1, pady=10)
        
        # Cycles before long break
        tk.Label(main_frame, text="Cycles before long break:", font=('Helvetica', 10)).grid(
            row=3, column=0, sticky='w', pady=10
        )
        self.cycles = tk.Spinbox(
            main_frame, from_=1, to=10, width=10,
            font=('Helvetica', 10)
        )
        self.cycles.delete(0, tk.END)
        self.cycles.insert(0, str(self.current_config['cycles_before_long_break']))
        self.cycles.grid(row=3, column=1, pady=10)
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        tk.Button(
            button_frame, text="Save", command=self._save,
            font=('Helvetica', 10, 'bold'), bg='#4A90E2', fg='white',
            padx=20, pady=5, relief=tk.FLAT, cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, text="Cancel", command=self.dialog.destroy,
            font=('Helvetica', 10), padx=20, pady=5,
            relief=tk.FLAT, cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
    
    def _save(self):
        """Save settings and close dialog."""
        try:
            self.result = {
                'work_duration': int(self.work_duration.get()) * 60,
                'short_break_duration': int(self.short_break.get()) * 60,
                'long_break_duration': int(self.long_break.get()) * 60,
                'cycles_before_long_break': int(self.cycles.get()),
            }
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
