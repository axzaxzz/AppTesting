"""
Synchronization Engine for Wave.AI
Coordinates Git sync, file watching, and version control
"""

import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional
import sys
import gc
import signal
import atexit

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.core.git_sync import GitSync
from src.core.version_control import VersionControl
from src.core.file_watcher import FileWatcher
from src.core.config_manager import config
from src.utils.logger import logger


class SyncEngine:
    """Main synchronization engine coordinating all operations"""
    
    def __init__(self):
        self.git_sync: Optional[GitSync] = None
        self.version_control: Optional[VersionControl] = None
        self.file_watcher: Optional[FileWatcher] = None
        
        self.is_running = False
        self.sync_thread: Optional[threading.Thread] = None
        self.last_sync_time = 0
        self.last_pull_time = 0
        self.sync_lock = threading.Lock()
        self._shutdown_event = threading.Event()
        
        self.stats = {
            "pulls": 0,
            "pushes": 0,
            "conflicts": 0,
            "errors": 0,
            "last_activity": None
        }
        
        # Register cleanup handlers
        atexit.register(self._cleanup)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self._shutdown_event.set()
        self.stop()
    
    def _cleanup(self):
        """Cleanup resources on exit"""
        try:
            if self.is_running:
                self.stop()
            
            # Force garbage collection
            gc.collect()
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def initialize(self) -> tuple[bool, str]:
        """Initialize all components"""
        try:
            # Validate configuration
            is_valid, errors = config.validate()
            if not is_valid:
                error_msg = "Configuration errors:\n" + "\n".join(errors)
                logger.error(error_msg)
                return False, error_msg
            
            # Initialize Git sync
            repo_url = config.get('github.repo_url')
            local_dir = config.get('local.code_directory')
            branch = config.get('github.branch', 'main')
            
            logger.info(f"Initializing Git sync for {repo_url}")
            self.git_sync = GitSync(repo_url, local_dir, branch)
            
            # Initialize version control
            self.version_control = VersionControl(self.git_sync)
            
            # Create initial checkpoint
            self.version_control.create_checkpoint("Initial checkpoint")
            
            # Initialize file watcher
            watch_patterns = config.get('local.watch_patterns', [])
            self.file_watcher = FileWatcher(local_dir, watch_patterns)
            self.file_watcher.set_change_callback(self._on_files_changed)
            
            logger.info("Wave.AI sync engine initialized successfully")
            return True, "Initialization successful"
            
        except Exception as e:
            error_msg = f"Initialization failed: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def start(self) -> tuple[bool, str]:
        """Start the synchronization engine"""
        if self.is_running:
            return False, "Sync engine is already running"
        
        if not self.git_sync:
            return False, "Sync engine not initialized. Call initialize() first."
        
        try:
            # Clear shutdown event
            self._shutdown_event.clear()
            
            # Start file watcher
            self.file_watcher.start()
            
            # Start sync thread
            self.is_running = True
            self.sync_thread = threading.Thread(target=self._sync_loop, daemon=False)  # Changed to non-daemon
            self.sync_thread.start()
            
            logger.info("Wave.AI sync engine started")
            return True, "Sync engine started"
            
        except Exception as e:
            error_msg = f"Failed to start sync engine: {e}"
            logger.error(error_msg)
            self.is_running = False
            return False, error_msg
    
    def stop(self) -> tuple[bool, str]:
        """Stop the synchronization engine with improved cleanup"""
        if not self.is_running:
            return False, "Sync engine is not running"
        
        try:
            logger.info("Stopping sync engine...")
            
            # Signal shutdown
            self._shutdown_event.set()
            self.is_running = False
            
            # Stop file watcher first
            if self.file_watcher:
                try:
                    self.file_watcher.stop()
                    logger.debug("File watcher stopped")
                except Exception as e:
                    logger.warning(f"Error stopping file watcher: {e}")
            
            # Wait for sync thread to finish with timeout
            if self.sync_thread and self.sync_thread.is_alive():
                logger.debug("Waiting for sync thread to finish...")
                self.sync_thread.join(timeout=5.0)  # 5 second timeout
                
                if self.sync_thread.is_alive():
                    logger.warning("Sync thread did not finish cleanly within timeout")
                else:
                    logger.debug("Sync thread finished cleanly")
            
            # Force cleanup
            self.sync_thread = None
            
            # Run garbage collection to free memory
            gc.collect()
            
            logger.info("Wave.AI sync engine stopped")
            return True, "Sync engine stopped"
            
        except Exception as e:
            error_msg = f"Error stopping sync engine: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def emergency_stop(self) -> tuple[bool, str]:
        """Emergency stop for when normal stop fails"""
        try:
            logger.warning("Emergency stop initiated")
            
            # Force stop everything
            self._shutdown_event.set()
            self.is_running = False
            
            # Force stop file watcher
            if self.file_watcher:
                try:
                    self.file_watcher._should_stop = True
                    if hasattr(self.file_watcher, '_observer') and self.file_watcher._observer:
                        self.file_watcher._observer.stop()
                except:
                    pass
            
            # Don't wait for thread, just mark as stopped
            self.sync_thread = None
            
            # Force garbage collection
            gc.collect()
            
            logger.warning("Emergency stop completed")
            return True, "Emergency stop completed"
            
        except Exception as e:
            logger.error(f"Emergency stop failed: {e}")
            return False, f"Emergency stop failed: {e}"
    
    def _sync_loop(self):
        """Main synchronization loop with improved memory management"""
        sync_interval = config.get('github.sync_interval', 30)
        auto_pull = config.get('github.auto_pull', True)
        
        logger.info(f"Sync loop started (interval: {sync_interval}s)")
        
        last_gc_time = time.time()
        gc_interval = 300  # Run garbage collection every 5 minutes
        
        while self.is_running and not self._shutdown_event.is_set():
            try:
                # Check for shutdown signal
                if self._shutdown_event.wait(timeout=1.0):  # Check every second
                    break
                
                current_time = time.time()
                
                # Check for remote changes and pull if auto_pull is enabled
                if auto_pull and (current_time - self.last_pull_time) >= sync_interval:
                    self._check_and_pull()
                
                # Check file watcher debounce
                if self.file_watcher:
                    self.file_watcher.check_debounce()
                
                # Periodic garbage collection to prevent memory leaks
                if current_time - last_gc_time > gc_interval:
                    gc.collect()
                    last_gc_time = current_time
                    logger.debug("Performed garbage collection")
                
                # Small sleep to prevent excessive CPU usage
                time.sleep(0.5)
                
            except Exception as e:
                if self.is_running:  # Only log if we're supposed to be running
                    logger.error(f"Error in sync loop: {e}")
                    self.stats["errors"] += 1
                
                # Wait longer after an error, but still check for shutdown
                if self._shutdown_event.wait(timeout=10):
                    break
        
        logger.info("Sync loop exited")
    
    def _check_and_pull(self):
        """Check for remote changes and pull if available"""
        current_time = time.time()
        
        try:
            # Use non-blocking lock to prevent hanging
            if not self.sync_lock.acquire(blocking=False):
                logger.debug("Sync already in progress, skipping pull check")
                return
            
            try:
                # Check for remote changes
                has_changes, commits_behind = self.git_sync.has_remote_changes()
                
                if has_changes:
                    logger.sync_event("REMOTE_CHANGES", f"{commits_behind} new commit(s) detected")
                    
                    # Pause file watcher during pull
                    if self.file_watcher:
                        self.file_watcher.pause()
                    
                    # Pull changes
                    success, message = self.git_sync.pull()
                    
                    if success:
                        self.stats["pulls"] += 1
                        self.stats["last_activity"] = datetime.now().isoformat()
                        logger.sync_event("PULL_SUCCESS", message)
                        
                        # Create checkpoint after successful pull
                        if self.version_control:
                            self.version_control.create_checkpoint(f"Auto-pull: {commits_behind} commit(s)")
                    else:
                        self.stats["errors"] += 1
                        logger.error(f"Pull failed: {message}")
                        
                        # Check for conflicts
                        has_conflicts, conflicted_files = self.git_sync.has_conflicts()
                        if has_conflicts:
                            self.stats["conflicts"] += 1
                            self._handle_conflict(conflicted_files)
                    
                    # Resume file watcher
                    if self.file_watcher:
                        self.file_watcher.resume()
                
                self.last_pull_time = current_time
                
            finally:
                self.sync_lock.release()
                
        except Exception as e:
            logger.error(f"Error during pull check: {e}")
            self.stats["errors"] += 1
            
            # Ensure file watcher is resumed even if there's an error
            if self.file_watcher:
                try:
                    self.file_watcher.resume()
                except:
                    pass
    
    def _on_files_changed(self, changed_files: list):
        """Callback when local files are changed"""
        if not config.get('github.auto_push', True):
            logger.debug("Auto-push is disabled, skipping commit")
            return
        
        try:
            # Use non-blocking lock to prevent hanging
            if not self.sync_lock.acquire(blocking=False):
                logger.debug("Sync already in progress, skipping file change handling")
                return
            
            try:
                logger.sync_event("LOCAL_CHANGES", f"{len(changed_files)} file(s) changed")
                
                # Create commit message
                commit_prefix = config.get('sync.commit_prefix', '[Wave.AI Auto]')
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Limit file list in message
                file_list = ", ".join([Path(f).name for f in changed_files[:5]])
                if len(changed_files) > 5:
                    file_list += f" and {len(changed_files) - 5} more"
                
                commit_msg = f"{commit_prefix} {timestamp}: {file_list}"
                
                # Commit and push
                success, result = self.git_sync.commit_and_push(commit_msg)
                
                if success:
                    self.stats["pushes"] += 1
                    self.stats["last_activity"] = datetime.now().isoformat()
                    logger.sync_event("PUSH_SUCCESS", result)
                    
                    # Create checkpoint
                    if self.version_control:
                        self.version_control.create_checkpoint(f"Auto-push: {len(changed_files)} file(s)")
                else:
                    self.stats["errors"] += 1
                    logger.error(f"Push failed: {result}")
            
            finally:
                self.sync_lock.release()
                
        except Exception as e:
            logger.error(f"Error handling file changes: {e}")
            self.stats["errors"] += 1
    
    def _handle_conflict(self, conflicted_files: list):
        """Handle merge conflicts"""
        logger.warning(f"Merge conflicts detected in {len(conflicted_files)} file(s):")
        for file in conflicted_files:
            logger.warning(f"  - {file}")
        
        # TODO: Implement conflict resolution UI
        # For now, just log the conflict
        conflict_strategy = config.get('sync.conflict_strategy', 'manual')
        
        if conflict_strategy == 'manual':
            logger.warning("Conflict strategy is 'manual'. Please resolve conflicts manually.")
        elif conflict_strategy == 'ours':
            logger.info("Using 'ours' strategy to resolve conflicts")
            # Keep local version
        elif conflict_strategy == 'theirs':
            logger.info("Using 'theirs' strategy to resolve conflicts")
            # Keep remote version
    
    def manual_sync(self) -> tuple[bool, str]:
        """Manually trigger a sync operation"""
        try:
            with self.sync_lock:
                # Check for local changes
                has_local, local_files = self.git_sync.has_local_changes()
                if has_local:
                    commit_msg = f"[Wave.AI Manual] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    success, result = self.git_sync.commit_and_push(commit_msg)
                    if not success:
                        return False, f"Failed to push local changes: {result}"
                
                # Pull remote changes
                success, message = self.git_sync.pull()
                if not success:
                    return False, f"Failed to pull: {message}"
                
                logger.sync_event("MANUAL_SYNC", "Manual sync completed")
                return True, "Manual sync successful"
                
        except Exception as e:
            error_msg = f"Manual sync failed: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_status(self) -> dict:
        """Get current status of sync engine"""
        status = {
            "is_running": self.is_running,
            "is_initialized": self.git_sync is not None,
            "stats": self.stats.copy(),
            "config": {
                "repo_url": config.get('github.repo_url'),
                "local_dir": config.get('local.code_directory'),
                "auto_pull": config.get('github.auto_pull'),
                "auto_push": config.get('github.auto_push'),
                "sync_interval": config.get('github.sync_interval')
            }
        }
        
        if self.git_sync:
            status["git_status"] = self.git_sync.get_status()
        
        if self.file_watcher:
            status["file_watcher"] = self.file_watcher.get_status()
        
        if self.version_control:
            status["version_control"] = self.version_control.get_current_position_info()
        
        return status
    
    def force_push(self) -> tuple[bool, str]:
        """Force push current state to GitHub"""
        try:
            with self.sync_lock:
                commit_msg = f"[Wave.AI Force] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                success, result = self.git_sync.commit_and_push(commit_msg)
                
                if success:
                    self.stats["pushes"] += 1
                    return True, "Force push successful"
                else:
                    return False, result
                    
        except Exception as e:
            return False, f"Force push failed: {e}"
    
    def force_pull(self) -> tuple[bool, str]:
        """Force pull from GitHub"""
        try:
            with self.sync_lock:
                # Pause file watcher
                if self.file_watcher:
                    self.file_watcher.pause()
                
                success, message = self.git_sync.pull()
                
                # Resume file watcher
                if self.file_watcher:
                    self.file_watcher.resume()
                
                if success:
                    self.stats["pulls"] += 1
                    return True, "Force pull successful"
                else:
                    return False, message
                    
        except Exception as e:
            return False, f"Force pull failed: {e}"


# Global sync engine instance
sync_engine = SyncEngine()
