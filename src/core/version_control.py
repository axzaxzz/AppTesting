"""
Version Control System for Wave.AI
Provides revert/forward capabilities and checkpoint management
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.logger import logger


class VersionControl:
    """Manages version history with revert/forward functionality"""
    
    def __init__(self, git_sync, history_file="logs/version_history.json"):
        self.git_sync = git_sync
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.history = self._load_history()
        self.current_position = len(self.history) - 1 if self.history else -1
    
    def _load_history(self) -> List[dict]:
        """Load version history from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load version history: {e}")
                return []
        return []
    
    def _save_history(self):
        """Save version history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save version history: {e}")
    
    def create_checkpoint(self, description: str = "") -> Tuple[bool, str]:
        """
        Create a checkpoint at the current state
        Returns: (success, checkpoint_id or error)
        """
        try:
            # Get current commit info
            status = self.git_sync.get_status()
            if "error" in status:
                return False, status["error"]
            
            latest_commit = status.get("latest_commit")
            if not latest_commit:
                return False, "No commits found"
            
            # Create checkpoint entry
            checkpoint = {
                "id": len(self.history),
                "commit_hash": latest_commit["hash"],
                "full_hash": self.git_sync.repo.head.commit.hexsha,
                "timestamp": datetime.now().isoformat(),
                "description": description or f"Checkpoint at {datetime.now().strftime('%H:%M:%S')}",
                "commit_message": latest_commit["message"],
                "author": latest_commit["author"]
            }
            
            # If we're not at the end of history, truncate future history
            if self.current_position < len(self.history) - 1:
                self.history = self.history[:self.current_position + 1]
            
            # Add checkpoint
            self.history.append(checkpoint)
            self.current_position = len(self.history) - 1
            self._save_history()
            
            logger.info(f"Created checkpoint: {checkpoint['description']}")
            return True, checkpoint['id']
            
        except Exception as e:
            error_msg = f"Failed to create checkpoint: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def revert(self, steps: int = 1) -> Tuple[bool, str]:
        """
        Revert to a previous version
        Args:
            steps: Number of steps to go back (default: 1)
        Returns: (success, message)
        """
        if not self.history:
            return False, "No version history available"
        
        new_position = self.current_position - steps
        
        if new_position < 0:
            return False, f"Cannot revert {steps} steps (only {self.current_position + 1} versions back)"
        
        target_checkpoint = self.history[new_position]
        
        try:
            # Create a safety checkpoint before reverting
            self.create_checkpoint(f"Safety checkpoint before revert")
            
            # Reset to target commit
            success, msg = self.git_sync.reset_to_commit(
                target_checkpoint['full_hash'],
                hard=True
            )
            
            if success:
                self.current_position = new_position
                logger.info(f"Reverted to: {target_checkpoint['description']}")
                return True, f"Reverted to: {target_checkpoint['description']}"
            else:
                return False, msg
                
        except Exception as e:
            error_msg = f"Revert failed: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def forward(self, steps: int = 1) -> Tuple[bool, str]:
        """
        Move forward to a newer version
        Args:
            steps: Number of steps to go forward (default: 1)
        Returns: (success, message)
        """
        if not self.history:
            return False, "No version history available"
        
        new_position = self.current_position + steps
        
        if new_position >= len(self.history):
            return False, f"Cannot go forward {steps} steps (only {len(self.history) - self.current_position - 1} versions ahead)"
        
        target_checkpoint = self.history[new_position]
        
        try:
            # Reset to target commit
            success, msg = self.git_sync.reset_to_commit(
                target_checkpoint['full_hash'],
                hard=True
            )
            
            if success:
                self.current_position = new_position
                logger.info(f"Moved forward to: {target_checkpoint['description']}")
                return True, f"Moved forward to: {target_checkpoint['description']}"
            else:
                return False, msg
                
        except Exception as e:
            error_msg = f"Forward failed: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def goto_checkpoint(self, checkpoint_id: int) -> Tuple[bool, str]:
        """
        Go to a specific checkpoint by ID
        Returns: (success, message)
        """
        if checkpoint_id < 0 or checkpoint_id >= len(self.history):
            return False, f"Invalid checkpoint ID: {checkpoint_id}"
        
        target_checkpoint = self.history[checkpoint_id]
        
        try:
            # Reset to target commit
            success, msg = self.git_sync.reset_to_commit(
                target_checkpoint['full_hash'],
                hard=True
            )
            
            if success:
                self.current_position = checkpoint_id
                logger.info(f"Moved to checkpoint {checkpoint_id}: {target_checkpoint['description']}")
                return True, f"Moved to: {target_checkpoint['description']}"
            else:
                return False, msg
                
        except Exception as e:
            error_msg = f"Goto checkpoint failed: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_history_summary(self, max_items: int = 20) -> List[dict]:
        """
        Get version history summary
        Returns: List of checkpoint summaries with current position marked
        """
        summary = []
        start_idx = max(0, len(self.history) - max_items)
        
        for i in range(start_idx, len(self.history)):
            checkpoint = self.history[i]
            summary.append({
                "id": checkpoint["id"],
                "description": checkpoint["description"],
                "timestamp": checkpoint["timestamp"],
                "commit_hash": checkpoint["commit_hash"],
                "is_current": i == self.current_position,
                "relative_position": i - self.current_position
            })
        
        return summary
    
    def get_current_position_info(self) -> Optional[dict]:
        """Get information about the current position in history"""
        if self.current_position < 0 or self.current_position >= len(self.history):
            return None
        
        current = self.history[self.current_position]
        return {
            "id": current["id"],
            "description": current["description"],
            "timestamp": current["timestamp"],
            "commit_hash": current["commit_hash"],
            "can_revert": self.current_position > 0,
            "can_forward": self.current_position < len(self.history) - 1,
            "steps_back_available": self.current_position,
            "steps_forward_available": len(self.history) - self.current_position - 1
        }
    
    def cleanup_old_checkpoints(self, max_checkpoints: int = 100):
        """
        Remove old checkpoints to limit history size
        Keeps the most recent max_checkpoints
        """
        if len(self.history) > max_checkpoints:
            # Keep the most recent checkpoints
            removed_count = len(self.history) - max_checkpoints
            self.history = self.history[-max_checkpoints:]
            
            # Adjust current position
            self.current_position = max(0, self.current_position - removed_count)
            
            # Renumber IDs
            for i, checkpoint in enumerate(self.history):
                checkpoint["id"] = i
            
            self._save_history()
            logger.info(f"Cleaned up {removed_count} old checkpoints")
    
    def export_history(self, export_path: str) -> Tuple[bool, str]:
        """Export version history to a file"""
        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "history": self.history,
                    "current_position": self.current_position,
                    "exported_at": datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
            
            return True, f"History exported to {export_path}"
        except Exception as e:
            return False, f"Export failed: {e}"
    
    def search_checkpoints(self, query: str) -> List[dict]:
        """Search checkpoints by description or commit message"""
        query_lower = query.lower()
        results = []
        
        for checkpoint in self.history:
            if (query_lower in checkpoint.get("description", "").lower() or
                query_lower in checkpoint.get("commit_message", "").lower()):
                results.append({
                    "id": checkpoint["id"],
                    "description": checkpoint["description"],
                    "commit_message": checkpoint["commit_message"],
                    "timestamp": checkpoint["timestamp"],
                    "commit_hash": checkpoint["commit_hash"]
                })
        
        return results

