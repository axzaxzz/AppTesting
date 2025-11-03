"""
File System Watcher for Wave.AI
Monitors local directory for file changes
"""

import time
from pathlib import Path
from typing import Set, Callable, Optional, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.logger import logger


class ChangeHandler(FileSystemEventHandler):
    """Handles file system events"""
    
    def __init__(self, callback: Callable, patterns: List[str], debounce_seconds: float = 2.0):
        super().__init__()
        self.callback = callback
        self.patterns = patterns
        self.debounce_seconds = debounce_seconds
        self.pending_changes: Set[str] = set()
        self.last_event_time = 0
    
    def _should_process_file(self, file_path: str) -> bool:
        """Check if file matches watch patterns"""
        path = Path(file_path)
        
        # Ignore .git directory
        if '.git' in path.parts:
            return False
        
        # Ignore temporary files
        if path.name.startswith('.') or path.name.endswith(('.tmp', '.swp', '~')):
            return False
        
        # Check against patterns
        if not self.patterns:
            return True
        
        for pattern in self.patterns:
            if path.match(pattern):
                return True
        
        return False
    
    def _process_event(self, event: FileSystemEvent):
        """Process a file system event"""
        if event.is_directory:
            return
        
        if not self._should_process_file(event.src_path):
            return
        
        # Add to pending changes
        self.pending_changes.add(event.src_path)
        self.last_event_time = time.time()
    
    def on_modified(self, event: FileSystemEvent):
        """Called when a file is modified"""
        self._process_event(event)
    
    def on_created(self, event: FileSystemEvent):
        """Called when a file is created"""
        self._process_event(event)
    
    def on_deleted(self, event: FileSystemEvent):
        """Called when a file is deleted"""
        self._process_event(event)
    
    def on_moved(self, event: FileSystemEvent):
        """Called when a file is moved"""
        self._process_event(event)
    
    def check_and_trigger(self):
        """Check if debounce period has passed and trigger callback"""
        if not self.pending_changes:
            return
        
        # Check if debounce period has passed
        if time.time() - self.last_event_time >= self.debounce_seconds:
            changes = list(self.pending_changes)
            self.pending_changes.clear()
            
            # Trigger callback with list of changed files
            try:
                self.callback(changes)
            except Exception as e:
                logger.error(f"Error in file change callback: {e}")


class FileWatcher:
    """Monitors local directory for file changes"""
    
    def __init__(self, watch_path: str, patterns: Optional[List[str]] = None, debounce_seconds: float = 2.0):
        self.watch_path = Path(watch_path)
        self.patterns = patterns or []
        self.debounce_seconds = debounce_seconds
        self.observer: Optional[Observer] = None
        self.handler: Optional[ChangeHandler] = None
        self.is_running = False
        self.change_callback: Optional[Callable] = None
    
    def set_change_callback(self, callback: Callable):
        """Set callback function to be called when changes are detected"""
        self.change_callback = callback
        if self.handler:
            self.handler.callback = callback
    
    def start(self):
        """Start watching for file changes"""
        if self.is_running:
            logger.warning("File watcher is already running")
            return
        
        if not self.watch_path.exists():
            logger.error(f"Watch path does not exist: {self.watch_path}")
            return
        
        if not self.change_callback:
            logger.error("No change callback set")
            return
        
        try:
            self.handler = ChangeHandler(
                self.change_callback,
                self.patterns,
                self.debounce_seconds
            )
            
            self.observer = Observer()
            self.observer.schedule(self.handler, str(self.watch_path), recursive=True)
            self.observer.start()
            
            self.is_running = True
            logger.info(f"File watcher started for: {self.watch_path}")
            logger.info(f"Watching patterns: {self.patterns if self.patterns else 'all files'}")
            
        except Exception as e:
            logger.error(f"Failed to start file watcher: {e}")
            self.is_running = False
    
    def stop(self):
        """Stop watching for file changes"""
        if not self.is_running:
            return
        
        try:
            if self.observer:
                self.observer.stop()
                self.observer.join(timeout=5)
            
            self.is_running = False
            logger.info("File watcher stopped")
            
        except Exception as e:
            logger.error(f"Error stopping file watcher: {e}")
    
    def check_debounce(self):
        """Check debounce timer and trigger callbacks if needed"""
        if self.handler:
            self.handler.check_and_trigger()
    
    def get_status(self) -> dict:
        """Get current watcher status"""
        return {
            "is_running": self.is_running,
            "watch_path": str(self.watch_path),
            "patterns": self.patterns,
            "debounce_seconds": self.debounce_seconds,
            "pending_changes": len(self.handler.pending_changes) if self.handler else 0
        }
    
    def pause(self):
        """Temporarily pause watching (doesn't stop the observer)"""
        if self.handler:
            self.handler.callback = lambda changes: None
            logger.info("File watcher paused")
    
    def resume(self):
        """Resume watching after pause"""
        if self.handler and self.change_callback:
            self.handler.callback = self.change_callback
            logger.info("File watcher resumed")
    
    def get_pending_changes(self) -> List[str]:
        """Get list of pending changes"""
        if self.handler:
            return list(self.handler.pending_changes)
        return []
    
    def clear_pending_changes(self):
        """Clear pending changes without triggering callback"""
        if self.handler:
            self.handler.pending_changes.clear()
            logger.debug("Cleared pending changes")

