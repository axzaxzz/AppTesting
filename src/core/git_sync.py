"""
Git Synchronization Module for Wave.AI
Handles all Git operations: clone, pull, push, commit, status
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple, Dict
import git
from git import Repo, GitCommandError
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.logger import logger


class GitSync:
    """Manages Git operations for synchronization"""
    
    def __init__(self, repo_url: str, local_path: str, branch: str = "main"):
        self.repo_url = repo_url
        self.local_path = Path(local_path)
        self.branch = branch
        self.repo: Optional[Repo] = None
        self._initialize_repo()
    
    def _initialize_repo(self):
        """Initialize or open Git repository"""
        try:
            if self.local_path.exists() and (self.local_path / ".git").exists():
                # Open existing repo
                self.repo = Repo(str(self.local_path))
                logger.info(f"Opened existing repository at {self.local_path}")
                
                # Fetch all branches to update local references
                try:
                    origin = self.repo.remote('origin')
                    logger.info("Fetching all branches from origin...")
                    origin.fetch()
                except Exception as e:
                    logger.warning(f"Could not fetch branches: {e}")
            else:
                # Clone new repo with all branches
                self.local_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Cloning repository from {self.repo_url} (all branches)...")
                
                # Clone without specifying branch to get all branches
                self.repo = Repo.clone_from(
                    self.repo_url, 
                    str(self.local_path),
                    multi_options=['--branch', self.branch]  # Checkout specific branch but fetch all
                )
                
                # Fetch all remote branches
                logger.info("Fetching all remote branches...")
                origin = self.repo.remote('origin')
                origin.fetch()
                
                # Create local tracking branches for all remote branches
                for ref in origin.refs:
                    # Skip HEAD reference
                    if ref.name == 'origin/HEAD':
                        continue
                    
                    branch_name = ref.name.replace('origin/', '')
                    
                    # Skip if local branch already exists
                    if branch_name in [b.name for b in self.repo.branches]:
                        continue
                    
                    # Create local tracking branch
                    try:
                        self.repo.create_head(branch_name, ref).set_tracking_branch(ref)
                        logger.info(f"Created local tracking branch: {branch_name}")
                    except Exception as e:
                        logger.warning(f"Could not create branch {branch_name}: {e}")
                
                logger.info(f"Repository cloned successfully to {self.local_path}")
            
            # Ensure we're on the correct branch
            if self.repo.active_branch.name != self.branch:
                self.repo.git.checkout(self.branch)
                
        except Exception as e:
            logger.error(f"Failed to initialize repository: {e}")
            raise
    
    def is_repo_initialized(self) -> bool:
        """Check if repository is properly initialized"""
        return self.repo is not None and self.local_path.exists()
    
    def get_status(self) -> dict:
        """Get current repository status"""
        if not self.is_repo_initialized():
            return {"error": "Repository not initialized"}
        
        try:
            # Check for uncommitted changes
            is_dirty = self.repo.is_dirty(untracked_files=True)
            
            # Get changed files
            changed_files = [item.a_path for item in self.repo.index.diff(None)]
            untracked_files = self.repo.untracked_files
            
            # Get current branch
            current_branch = self.repo.active_branch.name
            
            # Get latest commit
            latest_commit = None
            if self.repo.head.is_valid():
                commit = self.repo.head.commit
                latest_commit = {
                    "hash": commit.hexsha[:7],
                    "message": commit.message.strip(),
                    "author": str(commit.author),
                    "date": datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M:%S')
                }
            
            return {
                "is_dirty": is_dirty,
                "changed_files": changed_files,
                "untracked_files": untracked_files,
                "current_branch": current_branch,
                "latest_commit": latest_commit,
                "total_commits": len(list(self.repo.iter_commits()))
            }
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {"error": str(e)}
    
    def pull(self) -> Tuple[bool, str]:
        """
        Pull changes from remote repository
        Returns: (success, message)
        """
        if not self.is_repo_initialized():
            return False, "Repository not initialized"
        
        try:
            # Check for uncommitted changes
            if self.repo.is_dirty():
                logger.warning("Local changes detected, stashing before pull")
                self.repo.git.stash('save', 'Wave.AI auto-stash before pull')
            
            # Pull from remote
            origin = self.repo.remote('origin')
            pull_info = origin.pull(self.branch)
            
            # Restore stashed changes if any
            if self.repo.git.stash('list'):
                try:
                    self.repo.git.stash('pop')
                except GitCommandError as e:
                    logger.warning(f"Conflict when restoring stashed changes: {e}")
                    return False, "Conflict detected after pull. Please resolve manually."
            
            logger.git_event("PULL", f"Successfully pulled from {self.branch}")
            return True, "Pull successful"
            
        except GitCommandError as e:
            error_msg = f"Git pull failed: {e}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error during pull: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def commit(self, message: str, files: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Commit changes to repository
        Args:
            message: Commit message
            files: List of specific files to commit (None = all changes)
        Returns: (success, commit_hash or error_message)
        """
        if not self.is_repo_initialized():
            return False, "Repository not initialized"
        
        try:
            # Add files
            if files:
                self.repo.index.add(files)
            else:
                # Add all changes including untracked files
                self.repo.git.add(A=True)
            
            # Check if there's anything to commit
            if not self.repo.index.diff("HEAD") and not self.repo.untracked_files:
                logger.debug("No changes to commit")
                return True, "No changes to commit"
            
            # Commit
            commit = self.repo.index.commit(message)
            commit_hash = commit.hexsha[:7]
            
            logger.git_event("COMMIT", f"{commit_hash}: {message}")
            return True, commit_hash
            
        except Exception as e:
            error_msg = f"Commit failed: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def push(self) -> Tuple[bool, str]:
        """
        Push commits to remote repository
        Returns: (success, message)
        """
        if not self.is_repo_initialized():
            return False, "Repository not initialized"
        
        try:
            # Check if there are commits to push
            origin = self.repo.remote('origin')
            
            # Push to remote
            push_info = origin.push(self.branch)
            
            if push_info:
                logger.git_event("PUSH", f"Successfully pushed to {self.branch}")
                return True, "Push successful"
            else:
                return True, "No commits to push"
                
        except GitCommandError as e:
            error_msg = f"Git push failed: {e}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error during push: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def commit_and_push(self, message: str, files: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Commit and push changes in one operation
        Returns: (success, message)
        """
        # Commit
        success, result = self.commit(message, files)
        if not success:
            return False, result
        
        if result == "No changes to commit":
            return True, result
        
        # Push
        success, push_msg = self.push()
        return success, f"Commit {result}: {push_msg}"
    
    def has_remote_changes(self) -> Tuple[bool, int]:
        """
        Check if there are new commits on remote
        Returns: (has_changes, number_of_commits_behind)
        """
        if not self.is_repo_initialized():
            return False, 0
        
        try:
            # Fetch remote changes without merging
            origin = self.repo.remote('origin')
            origin.fetch()
            
            # Compare local and remote
            commits_behind = len(list(self.repo.iter_commits(f'{self.branch}..origin/{self.branch}')))
            
            return commits_behind > 0, commits_behind
            
        except Exception as e:
            logger.error(f"Error checking remote changes: {e}")
            return False, 0
    
    def has_local_changes(self) -> Tuple[bool, List[str]]:
        """
        Check if there are uncommitted local changes
        Returns: (has_changes, list_of_changed_files)
        """
        if not self.is_repo_initialized():
            return False, []
        
        try:
            if self.repo.is_dirty(untracked_files=True):
                changed = [item.a_path for item in self.repo.index.diff(None)]
                untracked = self.repo.untracked_files
                all_changes = changed + untracked
                return True, all_changes
            return False, []
            
        except Exception as e:
            logger.error(f"Error checking local changes: {e}")
            return False, []
    
    def get_commit_history(self, max_count: int = 50) -> List[dict]:
        """Get commit history"""
        if not self.is_repo_initialized():
            return []
        
        try:
            commits = []
            for commit in self.repo.iter_commits(self.branch, max_count=max_count):
                commits.append({
                    "hash": commit.hexsha[:7],
                    "full_hash": commit.hexsha,
                    "message": commit.message.strip(),
                    "author": str(commit.author),
                    "date": datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M:%S'),
                    "timestamp": commit.committed_date
                })
            return commits
        except Exception as e:
            logger.error(f"Error getting commit history: {e}")
            return []
    
    def reset_to_commit(self, commit_hash: str, hard: bool = False) -> Tuple[bool, str]:
        """
        Reset repository to a specific commit
        Args:
            commit_hash: Hash of commit to reset to
            hard: If True, discard all local changes
        Returns: (success, message)
        """
        if not self.is_repo_initialized():
            return False, "Repository not initialized"
        
        try:
            if hard:
                self.repo.git.reset('--hard', commit_hash)
                msg = f"Hard reset to {commit_hash}"
            else:
                self.repo.git.reset('--soft', commit_hash)
                msg = f"Soft reset to {commit_hash}"
            
            logger.git_event("RESET", msg)
            return True, msg
            
        except Exception as e:
            error_msg = f"Reset failed: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def has_conflicts(self) -> Tuple[bool, List[str]]:
        """
        Check if there are merge conflicts
        Returns: (has_conflicts, list_of_conflicted_files)
        """
        if not self.is_repo_initialized():
            return False, []
        
        try:
            # Get unmerged files (conflicts)
            unmerged = self.repo.index.unmerged_blobs()
            conflicted_files = list(unmerged.keys())
            
            return len(conflicted_files) > 0, conflicted_files
            
        except Exception as e:
            logger.error(f"Error checking conflicts: {e}")
            return False, []
    
    def get_all_branches(self) -> Dict[str, List[str]]:
        """
        Get all local and remote branches
        Returns: Dictionary with 'local' and 'remote' branch lists
        """
        if not self.is_repo_initialized():
            return {"local": [], "remote": []}
        
        try:
            local_branches = [branch.name for branch in self.repo.branches]
            
            remote_branches = []
            try:
                origin = self.repo.remote('origin')
                remote_branches = [ref.name.replace('origin/', '') 
                                 for ref in origin.refs 
                                 if ref.name != 'origin/HEAD']
            except Exception as e:
                logger.warning(f"Could not get remote branches: {e}")
            
            return {
                "local": local_branches,
                "remote": remote_branches,
                "current": self.repo.active_branch.name
            }
        except Exception as e:
            logger.error(f"Error getting branches: {e}")
            return {"local": [], "remote": []}

