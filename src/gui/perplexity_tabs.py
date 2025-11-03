"""
Perplexity Tab Manager for Wave.AI
Manages multiple Perplexity webview tabs
"""

import sys
from pathlib import Path
from typing import List, Dict

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.prompt_templates import PromptTemplates
from src.core.config_manager import config
from src.utils.logger import logger


class PerplexityTab:
    """Represents a single Perplexity tab"""
    
    def __init__(self, tab_id: int, title: str = "Perplexity"):
        self.tab_id = tab_id
        self.title = title
        self.url = config.get('perplexity.url', 'https://www.perplexity.ai')
        self.prompt_template = config.get('perplexity.custom_prompt_template', 'coding_assistant')
        self.history: List[str] = []
    
    def get_initial_prompt(self) -> str:
        """Get the initial prompt for this tab"""
        repo_url = config.get('github.repo_url', '')
        return PromptTemplates.create_custom_prompt(
            mode=self.prompt_template,
            repo_url=repo_url,
            context=f"Tab {self.tab_id + 1}"
        )
    
    def set_prompt_template(self, template_name: str):
        """Change the prompt template for this tab"""
        if template_name in PromptTemplates.list_templates():
            self.prompt_template = template_name
            logger.info(f"Tab {self.tab_id} template changed to: {template_name}")
        else:
            logger.warning(f"Unknown template: {template_name}")
    
    def add_to_history(self, message: str):
        """Add a message to this tab's history"""
        self.history.append(message)
    
    def get_info(self) -> Dict:
        """Get tab information"""
        return {
            'id': self.tab_id,
            'title': self.title,
            'url': self.url,
            'template': self.prompt_template,
            'history_length': len(self.history)
        }


class PerplexityTabManager:
    """Manages multiple Perplexity tabs"""
    
    def __init__(self):
        self.tabs: List[PerplexityTab] = []
        self.active_tab_id: int = 0
        self.max_tabs = config.get('ui.max_tabs', 5)
        
        # Create initial tab
        self._create_tab()
    
    def _create_tab(self, title: str = None) -> PerplexityTab:
        """Create a new tab"""
        tab_id = len(self.tabs)
        tab_title = title or f"Perplexity {tab_id + 1}"
        tab = PerplexityTab(tab_id, tab_title)
        self.tabs.append(tab)
        logger.info(f"Created tab {tab_id}: {tab_title}")
        return tab
    
    def create_tab(self, title: str = None, template: str = None) -> Dict:
        """
        Create a new tab (exposed to JavaScript)
        Returns: Tab information
        """
        if len(self.tabs) >= self.max_tabs:
            return {
                'success': False,
                'message': f'Maximum {self.max_tabs} tabs allowed'
            }
        
        tab = self._create_tab(title)
        
        if template:
            tab.set_prompt_template(template)
        
        return {
            'success': True,
            'tab': tab.get_info()
        }
    
    def close_tab(self, tab_id: int) -> Dict:
        """
        Close a tab (exposed to JavaScript)
        Returns: Success status
        """
        if len(self.tabs) <= 1:
            return {
                'success': False,
                'message': 'Cannot close the last tab'
            }
        
        if 0 <= tab_id < len(self.tabs):
            removed_tab = self.tabs.pop(tab_id)
            logger.info(f"Closed tab {tab_id}: {removed_tab.title}")
            
            # Renumber tabs
            for i, tab in enumerate(self.tabs):
                tab.tab_id = i
            
            # Adjust active tab if needed
            if self.active_tab_id >= len(self.tabs):
                self.active_tab_id = len(self.tabs) - 1
            
            return {'success': True}
        
        return {
            'success': False,
            'message': f'Invalid tab ID: {tab_id}'
        }
    
    def switch_tab(self, tab_id: int) -> Dict:
        """
        Switch to a different tab (exposed to JavaScript)
        Returns: Tab information
        """
        if 0 <= tab_id < len(self.tabs):
            self.active_tab_id = tab_id
            return {
                'success': True,
                'tab': self.tabs[tab_id].get_info()
            }
        
        return {
            'success': False,
            'message': f'Invalid tab ID: {tab_id}'
        }
    
    def get_active_tab(self) -> PerplexityTab:
        """Get the currently active tab"""
        if 0 <= self.active_tab_id < len(self.tabs):
            return self.tabs[self.active_tab_id]
        return self.tabs[0] if self.tabs else None
    
    def get_all_tabs(self) -> List[Dict]:
        """Get information about all tabs (exposed to JavaScript)"""
        return [tab.get_info() for tab in self.tabs]
    
    def set_tab_template(self, tab_id: int, template_name: str) -> Dict:
        """
        Set prompt template for a specific tab (exposed to JavaScript)
        Returns: Success status
        """
        if 0 <= tab_id < len(self.tabs):
            tab = self.tabs[tab_id]
            tab.set_prompt_template(template_name)
            return {
                'success': True,
                'prompt': tab.get_initial_prompt()
            }
        
        return {
            'success': False,
            'message': f'Invalid tab ID: {tab_id}'
        }
    
    def get_tab_prompt(self, tab_id: int) -> Dict:
        """
        Get the initial prompt for a tab (exposed to JavaScript)
        Returns: Prompt text
        """
        if 0 <= tab_id < len(self.tabs):
            tab = self.tabs[tab_id]
            return {
                'success': True,
                'prompt': tab.get_initial_prompt(),
                'template': tab.prompt_template
            }
        
        return {
            'success': False,
            'message': f'Invalid tab ID: {tab_id}'
        }
    
    def list_templates(self) -> List[Dict]:
        """
        List available prompt templates (exposed to JavaScript)
        Returns: List of templates with descriptions
        """
        templates = []
        for name in PromptTemplates.list_templates():
            templates.append({
                'name': name,
                'description': PromptTemplates.get_template_description(name)
            })
        return templates
    
    def rename_tab(self, tab_id: int, new_title: str) -> Dict:
        """
        Rename a tab (exposed to JavaScript)
        Returns: Success status
        """
        if 0 <= tab_id < len(self.tabs):
            self.tabs[tab_id].title = new_title
            logger.info(f"Renamed tab {tab_id} to: {new_title}")
            return {'success': True}
        
        return {
            'success': False,
            'message': f'Invalid tab ID: {tab_id}'
        }
    
    def get_tab_count(self) -> int:
        """Get the number of open tabs (exposed to JavaScript)"""
        return len(self.tabs)
    
    def can_create_tab(self) -> bool:
        """Check if a new tab can be created (exposed to JavaScript)"""
        return len(self.tabs) < self.max_tabs

