"""
Conflict Handler for Wave.AI
Utilities for detecting and resolving Git merge conflicts
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.logger import logger


class ConflictHandler:
    """Handles Git merge conflicts"""
    
    CONFLICT_MARKER_START = "<<<<<<< HEAD"
    CONFLICT_MARKER_MIDDLE = "======="
    CONFLICT_MARKER_END = ">>>>>>>"
    
    @staticmethod
    def detect_conflicts_in_file(file_path: str) -> bool:
        """
        Check if a file contains merge conflict markers
        Returns: True if conflicts found
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return (ConflictHandler.CONFLICT_MARKER_START in content and
                        ConflictHandler.CONFLICT_MARKER_MIDDLE in content and
                        ConflictHandler.CONFLICT_MARKER_END in content)
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return False
    
    @staticmethod
    def parse_conflict(file_path: str) -> List[Dict]:
        """
        Parse conflicts in a file
        Returns: List of conflict blocks with 'ours' and 'theirs' versions
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            conflicts = []
            i = 0
            
            while i < len(lines):
                if ConflictHandler.CONFLICT_MARKER_START in lines[i]:
                    # Found conflict start
                    conflict = {
                        'start_line': i,
                        'ours': [],
                        'theirs': [],
                        'file': file_path
                    }
                    
                    i += 1
                    # Read 'ours' version (HEAD)
                    while i < len(lines) and ConflictHandler.CONFLICT_MARKER_MIDDLE not in lines[i]:
                        conflict['ours'].append(lines[i])
                        i += 1
                    
                    i += 1  # Skip middle marker
                    # Read 'theirs' version (incoming)
                    while i < len(lines) and ConflictHandler.CONFLICT_MARKER_END not in lines[i]:
                        conflict['theirs'].append(lines[i])
                        i += 1
                    
                    conflict['end_line'] = i
                    conflicts.append(conflict)
                
                i += 1
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Error parsing conflicts in {file_path}: {e}")
            return []
    
    @staticmethod
    def resolve_conflict_ours(file_path: str) -> Tuple[bool, str]:
        """
        Resolve conflicts by keeping 'ours' (local) version
        Returns: (success, message)
        """
        try:
            conflicts = ConflictHandler.parse_conflict(file_path)
            if not conflicts:
                return True, "No conflicts found"
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Remove conflict markers and keep 'ours'
            new_lines = []
            i = 0
            conflict_idx = 0
            
            while i < len(lines):
                if conflict_idx < len(conflicts) and i == conflicts[conflict_idx]['start_line']:
                    # At conflict start, add 'ours' version
                    new_lines.extend(conflicts[conflict_idx]['ours'])
                    # Skip to after conflict end
                    i = conflicts[conflict_idx]['end_line'] + 1
                    conflict_idx += 1
                else:
                    new_lines.append(lines[i])
                    i += 1
            
            # Write resolved file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            logger.info(f"Resolved conflicts in {file_path} (kept 'ours')")
            return True, f"Kept local version, resolved {len(conflicts)} conflict(s)"
            
        except Exception as e:
            error_msg = f"Error resolving conflicts: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def resolve_conflict_theirs(file_path: str) -> Tuple[bool, str]:
        """
        Resolve conflicts by keeping 'theirs' (remote) version
        Returns: (success, message)
        """
        try:
            conflicts = ConflictHandler.parse_conflict(file_path)
            if not conflicts:
                return True, "No conflicts found"
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Remove conflict markers and keep 'theirs'
            new_lines = []
            i = 0
            conflict_idx = 0
            
            while i < len(lines):
                if conflict_idx < len(conflicts) and i == conflicts[conflict_idx]['start_line']:
                    # At conflict start, add 'theirs' version
                    new_lines.extend(conflicts[conflict_idx]['theirs'])
                    # Skip to after conflict end
                    i = conflicts[conflict_idx]['end_line'] + 1
                    conflict_idx += 1
                else:
                    new_lines.append(lines[i])
                    i += 1
            
            # Write resolved file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            logger.info(f"Resolved conflicts in {file_path} (kept 'theirs')")
            return True, f"Kept remote version, resolved {len(conflicts)} conflict(s)"
            
        except Exception as e:
            error_msg = f"Error resolving conflicts: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def get_conflict_summary(file_path: str) -> Dict:
        """
        Get summary of conflicts in a file
        Returns: Dictionary with conflict information
        """
        conflicts = ConflictHandler.parse_conflict(file_path)
        
        return {
            'file': file_path,
            'has_conflicts': len(conflicts) > 0,
            'conflict_count': len(conflicts),
            'conflicts': [
                {
                    'lines': f"{c['start_line']}-{c['end_line']}",
                    'ours_lines': len(c['ours']),
                    'theirs_lines': len(c['theirs'])
                }
                for c in conflicts
            ]
        }
    
    @staticmethod
    def scan_directory_for_conflicts(directory: str) -> List[str]:
        """
        Scan directory for files with conflicts
        Returns: List of file paths with conflicts
        """
        conflicted_files = []
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return conflicted_files
        
        # Scan all text files
        for file_path in dir_path.rglob('*'):
            if file_path.is_file():
                # Skip .git directory and binary files
                if '.git' in file_path.parts:
                    continue
                
                # Check for conflicts
                if ConflictHandler.detect_conflicts_in_file(str(file_path)):
                    conflicted_files.append(str(file_path))
                    logger.warning(f"Conflict detected in: {file_path}")
        
        return conflicted_files
    
    @staticmethod
    def create_conflict_report(conflicted_files: List[str]) -> str:
        """
        Create a human-readable conflict report
        Returns: Report text
        """
        if not conflicted_files:
            return "No conflicts detected."
        
        report = f"Merge Conflicts Detected ({len(conflicted_files)} file(s))\n"
        report += "=" * 60 + "\n\n"
        
        for file_path in conflicted_files:
            summary = ConflictHandler.get_conflict_summary(file_path)
            report += f"File: {file_path}\n"
            report += f"  Conflicts: {summary['conflict_count']}\n"
            
            for i, conflict in enumerate(summary['conflicts'], 1):
                report += f"    {i}. Lines {conflict['lines']} "
                report += f"(Ours: {conflict['ours_lines']} lines, "
                report += f"Theirs: {conflict['theirs_lines']} lines)\n"
            
            report += "\n"
        
        report += "Resolution Options:\n"
        report += "1. Manually edit files to resolve conflicts\n"
        report += "2. Use 'ours' strategy (keep local changes)\n"
        report += "3. Use 'theirs' strategy (keep remote changes)\n"
        report += "4. Revert to previous version\n"
        
        return report

