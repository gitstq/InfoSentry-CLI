"""
Terminal dashboard for InfoSentry
"""

import sys
import time
import select
from typing import Dict, Any, List
from .formatter import OutputFormatter


class Dashboard:
    """Terminal dashboard UI"""
    
    def __init__(self, refresh_interval: int = 60):
        self.refresh_interval = refresh_interval
        self.formatter = OutputFormatter(use_colors=True)
        self.running = False
        self.last_update = None
        self.items = []
        self.correlations = []
        self.patterns = []
    
    def update_data(self, items: List[Dict], correlations: List[Dict] = None, patterns: List[Dict] = None):
        """Update dashboard data"""
        self.items = items or []
        self.correlations = correlations or []
        self.patterns = patterns or []
        self.last_update = time.time()
    
    def render(self):
        """Render the dashboard"""
        # Clear screen
        print(self.formatter.clear_screen(), end='')
        
        # Header
        print(self.formatter.colorize("╔" + "═" * 78 + "╗", 'bright_blue'))
        print(self.formatter.colorize("║", 'bright_blue') + 
              self.formatter.colorize(" 📡 INFOSENTRY - Real-time Intelligence Dashboard ".center(78), 'bold') +
              self.formatter.colorize("║", 'bright_blue'))
        print(self.formatter.colorize("╠" + "═" * 78 + "╣", 'bright_blue'))
        
        # Status bar
        status = f" Events: {len(self.items)} | Correlations: {len(self.correlations)} | Patterns: {len(self.patterns)} "
        if self.last_update:
            elapsed = int(time.time() - self.last_update)
            status += f"| Last Update: {elapsed}s ago "
        print(self.formatter.colorize("║", 'bright_blue') + 
              self.formatter.colorize(status.center(78), 'dim') +
              self.formatter.colorize("║", 'bright_blue'))
        print(self.formatter.colorize("╚" + "═" * 78 + "╝", 'bright_blue'))
        print()
        
        # Summary section
        if self.items:
            print(self.formatter.format_summary(self.items, self.correlations, self.patterns))
            print()
        
        # Recent events
        if self.items:
            print(self.formatter.colorize("📰 RECENT EVENTS (Top 10)", 'bold'))
            print(self.formatter.colorize("─" * 80, 'dim'))
            for item in self.items[:10]:
                print(self.formatter.format_item(item, compact=True))
            print()
        else:
            print(self.formatter.colorize("No data available. Fetching...", 'dim'))
        
        # Footer
        print(self.formatter.colorize("─" * 80, 'dim'))
        print(self.formatter.colorize("Press 'q' to quit | 'r' to refresh | 's' for summary | 'a' for all events", 'dim'))
    
    def run(self, fetch_callback):
        """Run the dashboard with live updates"""
        self.running = True
        
        try:
            while self.running:
                # Fetch data
                try:
                    items, correlations, patterns = fetch_callback()
                    self.update_data(items, correlations, patterns)
                except Exception as e:
                    self.items = []
                    self.correlations = []
                    self.patterns = []
                
                # Render
                self.render()
                
                # Wait for input or refresh
                start_time = time.time()
                while time.time() - start_time < self.refresh_interval:
                    if self._check_input():
                        key = self._get_key()
                        if key == 'q':
                            self.running = False
                            break
                        elif key == 'r':
                            break  # Refresh immediately
                        elif key == 's':
                            self._show_detailed_summary()
                        elif key == 'a':
                            self._show_all_events()
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            pass
        finally:
            print(self.formatter.clear_screen(), end='')
            print(self.formatter.colorize("👋 Dashboard closed.", 'dim'))
    
    def _check_input(self) -> bool:
        """Check if there's input available"""
        try:
            return select.select([sys.stdin], [], [], 0)[0]
        except:
            return False
    
    def _get_key(self) -> str:
        """Get a single keypress"""
        try:
            import tty
            import termios
            
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(sys.stdin.fileno())
                return sys.stdin.read(1).lower()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except:
            return sys.stdin.read(1).lower() if self._check_input() else ''
    
    def _show_detailed_summary(self):
        """Show detailed summary view"""
        print(self.formatter.clear_screen(), end='')
        print(self.formatter.format_summary(self.items, self.correlations, self.patterns))
        print()
        input(self.formatter.colorize("Press Enter to continue...", 'dim'))
    
    def _show_all_events(self):
        """Show all events"""
        print(self.formatter.clear_screen(), end='')
        print(self.formatter.colorize("📰 ALL EVENTS", 'bold'))
        print(self.formatter.colorize("═" * 80, 'dim'))
        print()
        print(self.formatter.format_list(self.items, compact=False))
        print()
        input(self.formatter.colorize("Press Enter to continue...", 'dim'))
