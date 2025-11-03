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
import threading

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
        self._lock = threading.Lock()
        self._enabled = True
    
    def _should_process_file(self, file_path: str) -> bool:
        """Check if file matches watch patterns"""
        path = Path(file_path)
        
        # Ignore .git directory
        if '.git' in path.parts:
            return False
        
        # Ignore Wave.AI backup directories
        if '.wave-ai-backup' in path.parts:
            return False
        
        # Ignore temporary files and system files
        if (path.name.startswith('.') or 
            path.name.endswith(('.tmp', '.swp', '~', '.bak', '.log')) or
            path.name in ('Thumbs.db', '.DS_Store') or
            'EBWebView' in str(path) or
            'BrowserMetrics' in str(path)):
            return False
        
        # Ignore Python cache directories
        if '__pycache__' in path.parts or path.suffix == '.pyc':
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
        if not self._enabled:
            return
            
        if event.is_directory:
            return
        
        if not self._should_process_file(event.src_path):
            return
        
        with self._lock:
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
    
    def enable(self):
        """Enable event processing"""
        with self._lock:
            self._enabled = True
    
    def disable(self):
        """Disable event processing"""
        with self._lock:
            self._enabled = False
    
    def check_and_trigger(self):
        """Check if debounce period has passed and trigger callback"""
        if not self._enabled:
            return
            
        with self._lock:
            if not self.pending_changes:
                return
            
            # Check if debounce period has passed
            if time.time() - self.last_event_time >= self.debounce_seconds:
                changes = list(self.pending_changes)
                self.pending_changes.clear()
                
                # Trigger callback with list of changed files
                if self.callback:
                    try:
                        self.callback(changes)
                    except Exception as e:
                        logger.error(f"Error in file change callback: {e}")


class FileWatcher:
    """Monitors local directory for file changes with improved resource management"""
    
    def __init__(self, watch_path: str, patterns: Optional[List[str]] = None, debounce_seconds: float = 2.0):
        self.watch_path = Path(watch_path)
        self.patterns = patterns or []
        self.debounce_seconds = debounce_seconds
        self.observer: Optional[Observer] = None
        self.handler: Optional[ChangeHandler] = None
        self.is_running = False
        self.change_callback: Optional[Callable] = None
        self._should_stop = False
        self._lock = threading.Lock()
    
    def set_change_callback(self, callback: Callable):
        """Set callback function to be called when changes are detected"""
        with self._lock:
            self.change_callback = callback
            if self.handler:
                self.handler.callback = callback
    
    def start(self):
        """Start watching for file changes"""
        with self._lock:
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
                self._should_stop = False
                
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
                self._cleanup()
    
    def stop(self):
        """Stop watching for file changes with improved cleanup"""
        with self._lock:
            if not self.is_running:
                return
            
            try:
                self._should_stop = True
                
                # Disable the handler first
                if self.handler:
                    self.handler.disable()
                
                # Stop observer with timeout
                if self.observer:
                    try:
                        self.observer.stop()
                        self.observer.join(timeout=3.0)  # 3 second timeout
                        
                        if self.observer.is_alive():
                            logger.warning("File watcher observer did not stop cleanly")
                    except Exception as e:
                        logger.warning(f"Error stopping observer: {e}")
                
                self._cleanup()
                self.is_running = False
                logger.info("File watcher stopped")
                
            except Exception as e:
                logger.error(f"Error stopping file watcher: {e}")
                self._cleanup()
                self.is_running = False
    
    def _cleanup(self):
        """Clean up resources"""
        try:
            if self.handler:
                self.handler.disable()
                self.handler = None
            
            self.observer = None
            
        except Exception as e:
            logger.debug(f"Error during file watcher cleanup: {e}")
    
    def check_debounce(self):
        """Check debounce timer and trigger callbacks if needed"""
        if self.handler and not self._should_stop:
            self.handler.check_and_trigger()
    
    def get_status(self) -> dict:
        """Get current watcher status"""
        with self._lock:
            return {
                "is_running": self.is_running,
                "watch_path": str(self.watch_path),
                "patterns": self.patterns,
                "debounce_seconds": self.debounce_seconds,
                "pending_changes": len(self.handler.pending_changes) if self.handler else 0,
                "should_stop": self._should_stop
            }
    
    def pause(self):
        """Temporarily pause watching (disables event processing)"""
        if self.handler:
            self.handler.disable()
            logger.info("File watcher paused")
    
    def resume(self):
        """Resume watching after pause"""
        if self.handler and not self._should_stop:
            self.handler.enable()
            logger.info("File watcher resumed")
    
    def get_pending_changes(self) -> List[str]:
        """Get list of pending changes"""
        if self.handler:
            with self.handler._lock:
                return list(self.handler.pending_changes)
        return []
    
    def clear_pending_changes(self):
        """Clear pending changes without triggering callback"""
        if self.handler:
            with self.handler._lock:
                self.handler.pending_changes.clear()
                logger.debug("Cleared pending changes")
