"""
Emergency Stop Utility for Wave.AI
Provides emergency shutdown mechanisms to prevent freezing
"""

import os
import signal
import psutil
import threading
import time
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.logger import logger


class EmergencyStop:
    """Emergency stop mechanism for Wave.AI"""
    
    def __init__(self):
        self.stop_event = threading.Event()
        self.monitoring_thread = None
        self.max_memory_mb = 1024  # 1GB memory limit
        self.check_interval = 5  # Check every 5 seconds
        
    def start_monitoring(self):
        """Start monitoring system resources"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            return
        
        self.stop_event.clear()
        self.monitoring_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        self.monitoring_thread.start()
        logger.info("Emergency monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.stop_event.set()
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
        logger.info("Emergency monitoring stopped")
    
    def _monitor_resources(self):
        """Monitor system resources and trigger emergency stop if needed"""
        process = psutil.Process()
        
        while not self.stop_event.wait(self.check_interval):
            try:
                # Check memory usage
                memory_mb = process.memory_info().rss / 1024 / 1024
                
                if memory_mb > self.max_memory_mb:
                    logger.error(f"Memory usage critical: {memory_mb:.1f}MB > {self.max_memory_mb}MB")
                    self.trigger_emergency_stop("High memory usage")
                    break
                
                # Check for hung threads (basic check)
                thread_count = threading.active_count()
                if thread_count > 20:  # Arbitrary limit
                    logger.warning(f"High thread count detected: {thread_count}")
                
            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")
    
    def trigger_emergency_stop(self, reason: str):
        """Trigger emergency stop"""
        logger.critical(f"EMERGENCY STOP TRIGGERED: {reason}")
        
        try:
            # Import here to avoid circular imports
            from src.core.sync_engine import sync_engine
            
            # Try emergency stop first
            success, message = sync_engine.emergency_stop()
            if success:
                logger.info("Emergency stop completed successfully")
            else:
                logger.error(f"Emergency stop failed: {message}")
                self._force_kill_process()
        
        except Exception as e:
            logger.error(f"Error during emergency stop: {e}")
            self._force_kill_process()
    
    def _force_kill_process(self):
        """Last resort: force kill the process"""
        try:
            logger.critical("Force killing process...")
            os.kill(os.getpid(), signal.SIGTERM)
            
            # If SIGTERM doesn't work, use SIGKILL
            time.sleep(1)
            os.kill(os.getpid(), signal.SIGKILL)
            
        except Exception as e:
            logger.error(f"Error force killing process: {e}")
            # Last resort
            os._exit(1)
    
    def create_stop_file(self):
        """Create a stop file that can be checked by other processes"""
        try:
            stop_file = Path.cwd() / ".wave-ai-stop"
            stop_file.write_text(f"STOP\n{time.time()}")
            logger.info(f"Created emergency stop file: {stop_file}")
        except Exception as e:
            logger.error(f"Error creating stop file: {e}")
    
    def check_stop_file(self) -> bool:
        """Check if emergency stop file exists"""
        try:
            stop_file = Path.cwd() / ".wave-ai-stop"
            if stop_file.exists():
                logger.warning("Emergency stop file detected")
                stop_file.unlink()  # Remove the file
                return True
        except Exception as e:
            logger.error(f"Error checking stop file: {e}")
        
        return False
    
    def set_memory_limit(self, memory_mb: int):
        """Set memory limit for monitoring"""
        self.max_memory_mb = memory_mb
        logger.info(f"Memory limit set to {memory_mb}MB")


# Global emergency stop instance
emergency_stop = EmergencyStop()


def setup_emergency_handlers():
    """Setup emergency handlers for the application"""
    def signal_handler(signum, frame):
        logger.critical(f"Received signal {signum}, triggering emergency stop")
        emergency_stop.trigger_emergency_stop(f"Signal {signum}")
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start monitoring
    emergency_stop.start_monitoring()
    
    logger.info("Emergency handlers setup complete")


def cleanup_emergency_handlers():
    """Cleanup emergency handlers"""
    emergency_stop.stop_monitoring()
    logger.info("Emergency handlers cleaned up")
