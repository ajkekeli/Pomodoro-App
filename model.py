"""
Pomodoro Timer - Model
Handles all business logic and data management
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Callable


class PomodoroModel:
    """
    Model class for Pomodoro timer application.
    Manages timer state, sessions, and configuration.
    """
    
    # Timer states
    STATE_IDLE = "idle"
    STATE_RUNNING = "running"
    STATE_PAUSED = "paused"
    
    # Session types
    SESSION_WORK = "work"
    SESSION_SHORT_BREAK = "short_break"
    SESSION_LONG_BREAK = "long_break"
    
    def __init__(self):
        """Initialize the Pomodoro model with default settings."""
        # Configuration dictionary
        self.config: Dict = {
            'work_duration': 25 * 60,  # 25 minutes in seconds
            'short_break_duration': 5 * 60,  # 5 minutes
            'long_break_duration': 15 * 60,  # 15 minutes
            'cycles_before_long_break': 4,
            'auto_start_breaks': False,
            'auto_start_work': False,
        }
        
        # Current session state
        self.session_state: Dict = {
            'current_time': self.config['work_duration'],
            'session_type': self.SESSION_WORK,
            'state': self.STATE_IDLE,
            'current_cycle': 1,
            'total_cycles': self.config['cycles_before_long_break'],
            'completed_work_sessions': 0,
            'completed_break_sessions': 0,
        }
        
        # Statistics tracking
        self.statistics: Dict = {
            'total_work_time': 0,  # in seconds
            'total_break_time': 0,
            'sessions_completed': 0,
            'today_sessions': [],
            'last_reset': datetime.now().strftime('%Y-%m-%d'),
        }
        
        # Observer pattern for notifications
        self.observers: List[Callable] = []
        
        self._load_statistics()
    
    def add_observer(self, callback: Callable):
        """Add an observer to be notified of state changes."""
        if callback not in self.observers:
            self.observers.append(callback)
    
    def remove_observer(self, callback: Callable):
        """Remove an observer."""
        if callback in self.observers:
            self.observers.remove(callback)
    
    def notify_observers(self):
        """Notify all observers of state changes."""
        for callback in self.observers:
            callback()
    
    def start_timer(self):
        """Start the timer."""
        self.session_state['state'] = self.STATE_RUNNING
        self.notify_observers()
    
    def stop_timer(self):
        """Stop the timer and reset current session."""
        self.session_state['state'] = self.STATE_IDLE
        self._reset_current_session()
        self.notify_observers()
    
    def pause_timer(self):
        """Pause the timer."""
        self.session_state['state'] = self.STATE_PAUSED
        self.notify_observers()
    
    def tick(self):
        """
        Decrement timer by one second.
        Returns True if session is complete, False otherwise.
        """
        if self.session_state['state'] != self.STATE_RUNNING:
            return False
        
        self.session_state['current_time'] -= 1
        
        # Check if session is complete
        if self.session_state['current_time'] <= 0:
            self._complete_session()
            return True
        
        self.notify_observers()
        return False
    
    def _complete_session(self):
        """Handle session completion."""
        session_type = self.session_state['session_type']
        
        # Update statistics
        if session_type == self.SESSION_WORK:
            self.statistics['total_work_time'] += self.config['work_duration']
            self.session_state['completed_work_sessions'] += 1
            self.statistics['sessions_completed'] += 1
            
            # Log session
            self.statistics['today_sessions'].append({
                'type': 'work',
                'timestamp': datetime.now().isoformat(),
                'duration': self.config['work_duration']
            })
        else:
            duration = (self.config['short_break_duration'] 
                       if session_type == self.SESSION_SHORT_BREAK 
                       else self.config['long_break_duration'])
            self.statistics['total_break_time'] += duration
            self.session_state['completed_break_sessions'] += 1
            
            self.statistics['today_sessions'].append({
                'type': 'break',
                'timestamp': datetime.now().isoformat(),
                'duration': duration
            })
        
        # Move to next session
        self._next_session()
        self._save_statistics()
        self.notify_observers()
    
    def _next_session(self):
        """Transition to the next session type."""
        current_type = self.session_state['session_type']
        
        if current_type == self.SESSION_WORK:
            # Check if it's time for a long break
            if self.session_state['current_cycle'] >= self.config['cycles_before_long_break']:
                self.session_state['session_type'] = self.SESSION_LONG_BREAK
                self.session_state['current_time'] = self.config['long_break_duration']
                self.session_state['current_cycle'] = 1  # Reset cycle
            else:
                self.session_state['session_type'] = self.SESSION_SHORT_BREAK
                self.session_state['current_time'] = self.config['short_break_duration']
                self.session_state['current_cycle'] += 1
        else:
            # Break complete, go back to work
            self.session_state['session_type'] = self.SESSION_WORK
            self.session_state['current_time'] = self.config['work_duration']
        
        # Auto-start if configured
        if ((current_type == self.SESSION_WORK and self.config['auto_start_breaks']) or
            (current_type != self.SESSION_WORK and self.config['auto_start_work'])):
            self.session_state['state'] = self.STATE_RUNNING
        else:
            self.session_state['state'] = self.STATE_IDLE
    
    def _reset_current_session(self):
        """Reset the current session timer."""
        session_type = self.session_state['session_type']
        
        if session_type == self.SESSION_WORK:
            self.session_state['current_time'] = self.config['work_duration']
        elif session_type == self.SESSION_SHORT_BREAK:
            self.session_state['current_time'] = self.config['short_break_duration']
        else:
            self.session_state['current_time'] = self.config['long_break_duration']
    
    def reset_all(self):
        """Reset all session data and cycles."""
        self.session_state.update({
            'current_time': self.config['work_duration'],
            'session_type': self.SESSION_WORK,
            'state': self.STATE_IDLE,
            'current_cycle': 1,
            'completed_work_sessions': 0,
            'completed_break_sessions': 0,
        })
        self.notify_observers()
    
    def update_config(self, config_updates: Dict):
        """Update configuration settings."""
        self.config.update(config_updates)
        self.session_state['total_cycles'] = self.config['cycles_before_long_break']
        self._reset_current_session()
        self.notify_observers()
    
    def get_state_dict(self) -> Dict:
        """Return complete state as dictionary."""
        return {
            'config': self.config.copy(),
            'session': self.session_state.copy(),
            'statistics': self.statistics.copy(),
        }
    
    def get_progress_percentage(self) -> float:
        """Calculate current session progress as percentage."""
        session_type = self.session_state['session_type']
        current_time = self.session_state['current_time']
        
        if session_type == self.SESSION_WORK:
            total_time = self.config['work_duration']
        elif session_type == self.SESSION_SHORT_BREAK:
            total_time = self.config['short_break_duration']
        else:
            total_time = self.config['long_break_duration']
        
        return ((total_time - current_time) / total_time) * 100 if total_time > 0 else 0
    
    def _save_statistics(self):
        """Save statistics to file."""
        try:
            with open('pomodoro_stats.json', 'w') as f:
                json.dump(self.statistics, f, indent=2)
        except Exception as e:
            print(f"Error saving statistics: {e}")
    
    def _load_statistics(self):
        """Load statistics from file."""
        try:
            if os.path.exists('pomodoro_stats.json'):
                with open('pomodoro_stats.json', 'r') as f:
                    saved_stats = json.load(f)
                    
                # Check if we need to reset daily stats
                today = datetime.now().strftime('%Y-%m-%d')
                if saved_stats.get('last_reset') != today:
                    saved_stats['today_sessions'] = []
                    saved_stats['last_reset'] = today
                
                self.statistics.update(saved_stats)
        except Exception as e:
            print(f"Error loading statistics: {e}")
    
    def format_time(self, seconds: int) -> str:
        """Format seconds as MM:SS."""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
