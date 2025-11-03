"""
Account Manager for Wave.AI
Manages multiple GitHub and Perplexity accounts
"""

import json
from pathlib import Path
from typing import List, Dict, Optional


class AccountManager:
    """Manages user accounts for GitHub and Perplexity"""
    
    def __init__(self, accounts_file="config/accounts.json"):
        self.accounts_file = Path(accounts_file)
        self.accounts_file.parent.mkdir(parents=True, exist_ok=True)
        self.accounts = self._load_accounts()
    
    def _load_accounts(self) -> Dict:
        """Load accounts from file"""
        if self.accounts_file.exists():
            try:
                with open(self.accounts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return self._default_accounts()
        return self._default_accounts()
    
    def _default_accounts(self) -> Dict:
        """Get default account structure"""
        return {
            "github_accounts": [],
            "perplexity_profiles": [],
            "active_github": None,
            "active_perplexity": None
        }
    
    def _save_accounts(self):
        """Save accounts to file"""
        with open(self.accounts_file, 'w', encoding='utf-8') as f:
            json.dump(self.accounts, f, indent=2, ensure_ascii=False)
    
    # GitHub Account Management
    def add_github_account(self, username: str, repo_url: str, local_dir: str) -> bool:
        """Add a GitHub account"""
        account = {
            "id": len(self.accounts["github_accounts"]),
            "username": username,
            "repo_url": repo_url,
            "local_dir": local_dir
        }
        self.accounts["github_accounts"].append(account)
        
        # Set as active if it's the first account
        if len(self.accounts["github_accounts"]) == 1:
            self.accounts["active_github"] = account["id"]
        
        self._save_accounts()
        return True
    
    def remove_github_account(self, account_id: int) -> bool:
        """Remove a GitHub account"""
        self.accounts["github_accounts"] = [
            acc for acc in self.accounts["github_accounts"] 
            if acc["id"] != account_id
        ]
        
        # Clear active if it was the removed account
        if self.accounts["active_github"] == account_id:
            self.accounts["active_github"] = None
            if self.accounts["github_accounts"]:
                self.accounts["active_github"] = self.accounts["github_accounts"][0]["id"]
        
        self._save_accounts()
        return True
    
    def get_github_accounts(self) -> List[Dict]:
        """Get all GitHub accounts"""
        return self.accounts["github_accounts"]
    
    def get_active_github(self) -> Optional[Dict]:
        """Get active GitHub account"""
        active_id = self.accounts.get("active_github")
        if active_id is not None:
            for acc in self.accounts["github_accounts"]:
                if acc["id"] == active_id:
                    return acc
        return None
    
    def set_active_github(self, account_id: int) -> bool:
        """Set active GitHub account"""
        for acc in self.accounts["github_accounts"]:
            if acc["id"] == account_id:
                self.accounts["active_github"] = account_id
                self._save_accounts()
                return True
        return False
    
    # Perplexity Profile Management
    def add_perplexity_profile(self, name: str, notes: str = "") -> bool:
        """Add a Perplexity profile"""
        profile = {
            "id": len(self.accounts["perplexity_profiles"]),
            "name": name,
            "notes": notes
        }
        self.accounts["perplexity_profiles"].append(profile)
        
        # Set as active if it's the first profile
        if len(self.accounts["perplexity_profiles"]) == 1:
            self.accounts["active_perplexity"] = profile["id"]
        
        self._save_accounts()
        return True
    
    def remove_perplexity_profile(self, profile_id: int) -> bool:
        """Remove a Perplexity profile"""
        self.accounts["perplexity_profiles"] = [
            prof for prof in self.accounts["perplexity_profiles"] 
            if prof["id"] != profile_id
        ]
        
        # Clear active if it was the removed profile
        if self.accounts["active_perplexity"] == profile_id:
            self.accounts["active_perplexity"] = None
            if self.accounts["perplexity_profiles"]:
                self.accounts["active_perplexity"] = self.accounts["perplexity_profiles"][0]["id"]
        
        self._save_accounts()
        return True
    
    def get_perplexity_profiles(self) -> List[Dict]:
        """Get all Perplexity profiles"""
        return self.accounts["perplexity_profiles"]
    
    def get_active_perplexity(self) -> Optional[Dict]:
        """Get active Perplexity profile"""
        active_id = self.accounts.get("active_perplexity")
        if active_id is not None:
            for prof in self.accounts["perplexity_profiles"]:
                if prof["id"] == active_id:
                    return prof
        return None
    
    def set_active_perplexity(self, profile_id: int) -> bool:
        """Set active Perplexity profile"""
        for prof in self.accounts["perplexity_profiles"]:
            if prof["id"] == profile_id:
                self.accounts["active_perplexity"] = profile_id
                self._save_accounts()
                return True
        return False


# Global account manager instance
account_manager = AccountManager()

