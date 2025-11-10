"""
History Viewer for Pomodoro Timer
Shows all past sessions with dates and times
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Dict, List

class HistoryWindow:
    """Window to display session history."""
    
    def __init__(self, parent, statistics: Dict):
        """Initialize history window."""
        self.statistics = statistics
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("📜 Session History")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        # Make it modal
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
        self._load_history()
    
    def _create_widgets(self):
        """Create all widgets."""
        # Title frame
        title_frame = tk.Frame(self.window, bg='#4A90E2', height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="📜 Session History",
            font=('Helvetica', 18, 'bold'),
            bg='#4A90E2',
            fg='white'
        ).pack(pady=15)
        
        # Summary frame
        summary_frame = tk.Frame(self.window, bg='#F0F4F8', height=80)
        summary_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Summary labels
        stats_container = tk.Frame(summary_frame, bg='#F0F4F8')
        stats_container.pack(expand=True)
        
        # Total sessions
        self._create_stat_box(
            stats_container, 
            "Total Sessions", 
            str(self.statistics['sessions_completed']),
            '#4A90E2'
        ).pack(side=tk.LEFT, padx=10)
        
        # Total work time
        work_hours = self.statistics['total_work_time'] / 3600
        self._create_stat_box(
            stats_container,
            "Work Time",
            f"{work_hours:.1f}h",
            '#27AE60'
        ).pack(side=tk.LEFT, padx=10)
        
        # Total break time
        break_hours = self.statistics['total_break_time'] / 3600
        self._create_stat_box(
            stats_container,
            "Break Time",
            f"{break_hours:.1f}h",
            '#E67E22'
        ).pack(side=tk.LEFT, padx=10)
        
        # Today's sessions
        today_count = len(self.statistics['today_sessions'])
        self._create_stat_box(
            stats_container,
            "Today's Sessions",
            str(today_count),
            '#9B59B6'
        ).pack(side=tk.LEFT, padx=10)
        
        # Treeview frame
        tree_frame = tk.Frame(self.window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=('Date', 'Time', 'Type', 'Name', 'Duration'),
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            height=15
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Define columns
        self.tree.heading('Date', text='📅 Date')
        self.tree.heading('Time', text='🕐 Time')
        self.tree.heading('Type', text='📋 Type')
        self.tree.heading('Name', text='✏ Session Name')
        self.tree.heading('Duration', text='⏱ Duration')
        
        self.tree.column('Date', width=120)
        self.tree.column('Time', width=100)
        self.tree.column('Type', width=100)
        self.tree.column('Name', width=250)
        self.tree.column('Duration', width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for colors
        self.tree.tag_configure('work', background='#E3F2FD')
        self.tree.tag_configure('break', background='#E8F5E9')
        
        # Close button
        close_btn = tk.Button(
            self.window,
            text="✓ Close",
            font=('Helvetica', 12, 'bold'),
            bg='#4A90E2',
            fg='white',
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor='hand2',
            command=self.window.destroy
        )
        close_btn.pack(pady=20)
    
    def _create_stat_box(self, parent, label, value, color):
        """Create a statistics box."""
        box = tk.Frame(parent, bg='white', relief=tk.RIDGE, bd=2)
        
        tk.Label(
            box,
            text=label,
            font=('Helvetica', 9),
            bg='white',
            fg='#666'
        ).pack(pady=(10, 0))
        
        tk.Label(
            box,
            text=value,
            font=('Helvetica', 20, 'bold'),
            bg='white',
            fg=color
        ).pack(pady=(0, 10))
        
        box.pack_propagate(False)
        box.config(width=150, height=80)
        
        return box
    
    def _load_history(self):
        """Load all sessions into treeview."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get all sessions (reversed to show newest first)
        sessions = self.statistics['today_sessions'][::-1]
        
        for session in sessions:
            # Parse timestamp
            try:
                dt = datetime.fromisoformat(session['timestamp'])
                date_str = dt.strftime('%Y-%m-%d')
                time_str = dt.strftime('%H:%M:%S')
            except:
                date_str = 'Unknown'
                time_str = 'Unknown'
            
            # Get session details
            session_type = '💼 Work' if session['type'] == 'work' else '☕ Break'
            session_name = session.get('name', 'Untitled')
            duration = session['duration']
            duration_str = f"{duration // 60}m {duration % 60}s"
            
            # Insert into treeview
            tag = 'work' if session['type'] == 'work' else 'break'
            self.tree.insert(
                '',
                tk.END,
                values=(date_str, time_str, session_type, session_name, duration_str),
                tags=(tag,)
            )