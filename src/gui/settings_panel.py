"""
Settings Panel API for Wave.AI
Provides JavaScript API for settings management
"""

import sys
from pathlib import Path
from typing import Dict, Any

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.core.config_manager import config
from src.core.sync_engine import sync_engine
from src.utils.logger import logger
from src.utils.account_manager import account_manager


class SettingsAPI:
    """API for settings panel interactions"""
    
    def get_settings(self) -> Dict[str, Any]:
        """
        Get current settings (exposed to JavaScript)
        Returns: All configuration values
        """
        return {
            'github': {
                'repo_url': config.get('github.repo_url', ''),
                'branch': config.get('github.branch', 'main'),
                'auto_push': config.get('github.auto_push', True),
                'auto_pull': config.get('github.auto_pull', True),
                'sync_interval': config.get('github.sync_interval', 30)
            },
            'local': {
                'code_directory': config.get('local.code_directory', ''),
                'watch_patterns': config.get('local.watch_patterns', [])
            },
            'ui': {
                'theme': config.get('ui.theme', 'dark'),
                'max_tabs': config.get('ui.max_tabs', 5),
                'show_notifications': config.get('ui.show_notifications', True)
            },
            'perplexity': {
                'url': config.get('perplexity.url', 'https://www.perplexity.ai'),
                'custom_prompt_enabled': config.get('perplexity.custom_prompt_enabled', True),
                'custom_prompt_template': config.get('perplexity.custom_prompt_template', 'coding_assistant')
            }
        }
    
    def save_settings(self, settings: Dict[str, Any]) -> Dict:
        """
        Save settings (exposed to JavaScript)
        Args:
            settings: Dictionary of settings to save
        Returns: Success status
        """
        try:
            logger.info(f"Saving settings: {settings}")
            
            # Update GitHub settings
            if 'repo_url' in settings:
                config.set('github.repo_url', settings['repo_url'], save_immediately=False)
            if 'branch' in settings:
                config.set('github.branch', settings['branch'], save_immediately=False)
            if 'sync_interval' in settings:
                try:
                    interval = int(settings['sync_interval'])
                    if interval < 10:
                        interval = 10  # Minimum 10 seconds
                    config.set('github.sync_interval', interval, save_immediately=False)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid sync_interval, using default: {e}")
                    config.set('github.sync_interval', 30, save_immediately=False)
            if 'auto_push' in settings:
                config.set('github.auto_push', bool(settings['auto_push']), save_immediately=False)
            if 'auto_pull' in settings:
                config.set('github.auto_pull', bool(settings['auto_pull']), save_immediately=False)
            
            # Update local settings
            if 'local_dir' in settings or 'localDir' in settings:
                local_dir = settings.get('local_dir') or settings.get('localDir')
                if local_dir:
                    config.set('local.code_directory', str(local_dir), save_immediately=False)
            if 'watch_patterns' in settings:
                config.set('local.watch_patterns', settings['watch_patterns'], save_immediately=False)
            
            # Update UI settings
            if 'theme' in settings:
                theme = str(settings['theme'])
                config.set('ui.theme', theme, save_immediately=False)
                logger.info(f"Theme changed to: {theme}")
            if 'max_tabs' in settings:
                try:
                    max_tabs = int(settings['max_tabs'])
                    config.set('ui.max_tabs', max_tabs, save_immediately=False)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid max_tabs, using default: {e}")
            
            # Update Perplexity settings
            if 'perplexity_url' in settings:
                config.set('perplexity.url', settings['perplexity_url'], save_immediately=False)
            if 'custom_prompt_template' in settings:
                config.set('perplexity.custom_prompt_template', settings['custom_prompt_template'], save_immediately=False)
            
            # Save all changes to disk
            config.save()
            
            logger.info("Settings saved successfully")
            return {'success': True, 'message': 'Settings saved successfully'}
            
        except Exception as e:
            error_msg = f"Failed to save settings: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {'success': False, 'message': error_msg}
    
    def validate_settings(self) -> Dict:
        """
        Validate current settings (exposed to JavaScript)
        Returns: Validation results
        """
        is_valid, errors = config.validate()
        return {
            'is_valid': is_valid,
            'errors': errors
        }
    
    def reset_to_defaults(self) -> Dict:
        """
        Reset settings to defaults (exposed to JavaScript)
        Returns: Success status
        """
        try:
            config.reset_to_defaults()
            logger.info("Settings reset to defaults")
            return {'success': True, 'message': 'Settings reset to defaults'}
        except Exception as e:
            error_msg = f"Failed to reset settings: {e}"
            logger.error(error_msg)
            return {'success': False, 'message': error_msg}
    
    def get_status(self) -> Dict:
        """
        Get sync engine status (exposed to JavaScript)
        Returns: Current status
        """
        return sync_engine.get_status()
    
    def start_sync(self) -> Dict:
        """
        Start sync engine (exposed to JavaScript)
        Returns: Success status (returns immediately, initialization happens in background)
        """
        try:
            # Check if configured
            if not config.is_configured():
                error_msg = "Please configure GitHub repository URL and local directory in Settings first."
                logger.error(error_msg)
                return {'success': False, 'message': error_msg}
            
            # Check if already running
            if sync_engine.is_running:
                return {'success': True, 'message': 'Sync engine is already running'}
            
            # Initialize if needed - but do it in background thread to avoid blocking
            if not sync_engine.git_sync:
                logger.info("Starting sync engine initialization in background...")
                # Run initialization in background thread to avoid blocking UI
                import threading
                
                def init_and_start():
                    try:
                        logger.info("Initializing sync engine in background...")
                        success, message = sync_engine.initialize()
                        if success:
                            logger.info("Starting sync engine...")
                            start_success, start_message = sync_engine.start()
                            if start_success:
                                logger.info("Sync engine started successfully")
                            else:
                                logger.error(f"Failed to start sync: {start_message}")
                        else:
                            logger.error(f"Initialization failed: {message}")
                    except Exception as e:
                        logger.error(f"Error during background initialization: {e}", exc_info=True)
                
                # Start initialization in background
                init_thread = threading.Thread(target=init_and_start, daemon=True)
                init_thread.start()
                
                # Return immediately - initialization is happening in background
                return {'success': True, 'message': 'Sync engine initialization started in background. This may take a moment.'}
            else:
                # Already initialized, just start
                logger.info("Starting sync engine...")
                success, message = sync_engine.start()
                if success:
                    logger.info("Sync engine started successfully")
                else:
                    logger.error(f"Failed to start sync: {message}")
                return {'success': success, 'message': message}
            
        except Exception as e:
            error_msg = f"Failed to start sync: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {'success': False, 'message': error_msg}
    
    def stop_sync(self) -> Dict:
        """
        Stop sync engine (exposed to JavaScript)
        Returns: Success status
        """
        try:
            success, message = sync_engine.stop()
            return {'success': success, 'message': message}
        except Exception as e:
            error_msg = f"Failed to stop sync: {e}"
            logger.error(error_msg)
            return {'success': False, 'message': error_msg}
    
    def manual_sync(self) -> Dict:
        """
        Trigger manual sync (exposed to JavaScript)
        Returns: Success status
        """
        try:
            success, message = sync_engine.manual_sync()
            return {'success': success, 'message': message}
        except Exception as e:
            error_msg = f"Manual sync failed: {e}"
            logger.error(error_msg)
            return {'success': False, 'message': error_msg}
    
    def force_pull(self) -> Dict:
        """
        Force pull from GitHub (exposed to JavaScript)
        Returns: Success status
        """
        try:
            success, message = sync_engine.force_pull()
            return {'success': success, 'message': message}
        except Exception as e:
            error_msg = f"Force pull failed: {e}"
            logger.error(error_msg)
            return {'success': False, 'message': error_msg}
    
    def force_push(self) -> Dict:
        """
        Force push to GitHub (exposed to JavaScript)
        Returns: Success status
        """
        try:
            success, message = sync_engine.force_push()
            return {'success': success, 'message': message}
        except Exception as e:
            error_msg = f"Force push failed: {e}"
            logger.error(error_msg)
            return {'success': False, 'message': error_msg}
    
    def get_version_history(self, max_items: int = 20) -> Dict:
        """
        Get version history (exposed to JavaScript)
        Returns: History data
        """
        if sync_engine.version_control:
            history = sync_engine.version_control.get_history_summary(max_items)
            return {'success': True, 'history': history}
        return {'success': False, 'message': 'Version control not initialized'}
    
    def revert(self, steps: int = 1) -> Dict:
        """
        Revert to previous version (exposed to JavaScript)
        Returns: Success status
        """
        if sync_engine.version_control:
            success, message = sync_engine.version_control.revert(steps)
            return {'success': success, 'message': message}
        return {'success': False, 'message': 'Version control not initialized'}
    
    def forward(self, steps: int = 1) -> Dict:
        """
        Move forward to newer version (exposed to JavaScript)
        Returns: Success status
        """
        if sync_engine.version_control:
            success, message = sync_engine.version_control.forward(steps)
            return {'success': success, 'message': message}
        return {'success': False, 'message': 'Version control not initialized'}
    
    def goto_checkpoint(self, checkpoint_id: int) -> Dict:
        """
        Go to specific checkpoint (exposed to JavaScript)
        Returns: Success status
        """
        if sync_engine.version_control:
            success, message = sync_engine.version_control.goto_checkpoint(checkpoint_id)
            return {'success': success, 'message': message}
        return {'success': False, 'message': 'Version control not initialized'}
    
    def create_checkpoint(self, description: str = "") -> Dict:
        """
        Create manual checkpoint (exposed to JavaScript)
        Returns: Success status with checkpoint ID
        """
        if sync_engine.version_control:
            success, checkpoint_id = sync_engine.version_control.create_checkpoint(description)
            return {'success': success, 'checkpoint_id': checkpoint_id if success else None}
        return {'success': False, 'message': 'Version control not initialized'}
    
    def browse_directory(self) -> str:
        """
        Open directory browser dialog (exposed to JavaScript)
        Returns: Selected directory path
        """
        # This would need to be implemented with a file dialog
        # For now, return empty string
        # TODO: Implement file dialog using tkinter or similar
        return ""
    
    def openPerplexityBrowser(self) -> Dict:
        """
        Open Perplexity in default browser (exposed to JavaScript)
        Returns: Success status
        """
        try:
            import webbrowser
            perplexity_url = config.get('perplexity.url', 'https://www.perplexity.ai')
            webbrowser.open(perplexity_url)
            logger.info(f"Opened Perplexity in browser: {perplexity_url}")
            return {'success': True, 'message': 'Opened Perplexity in browser'}
        except Exception as e:
            error_msg = f"Failed to open browser: {e}"
            logger.error(error_msg)
            return {'success': False, 'message': error_msg}
    
    # Account Management Methods
    def getAccounts(self) -> Dict:
        """Get all accounts (exposed to JavaScript)"""
        return account_manager.accounts
    
    def addGithubAccount(self, username: str, repo_url: str, local_dir: str) -> Dict:
        """Add GitHub account (exposed to JavaScript)"""
        try:
            success = account_manager.add_github_account(username, repo_url, local_dir)
            if success:
                return {'success': True}
            return {'success': False, 'message': 'Failed to add account'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def removeGithubAccount(self, account_id: int) -> Dict:
        """Remove GitHub account (exposed to JavaScript)"""
        try:
            success = account_manager.remove_github_account(account_id)
            return {'success': success}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def switchGithubAccount(self, account_id: int) -> Dict:
        """Switch active GitHub account (exposed to JavaScript)"""
        try:
            success = account_manager.set_active_github(account_id)
            if success:
                # Update config with new account details
                account = account_manager.get_active_github()
                if account:
                    config.set('github.repo_url', account['repo_url'], save_immediately=False)
                    config.set('local.code_directory', account['local_dir'], save_immediately=False)
                    config.save()
                return {'success': True}
            return {'success': False, 'message': 'Account not found'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def addPerplexityProfile(self, name: str, notes: str = "") -> Dict:
        """Add Perplexity profile (exposed to JavaScript)"""
        try:
            success = account_manager.add_perplexity_profile(name, notes)
            return {'success': success}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def removePerplexityProfile(self, profile_id: int) -> Dict:
        """Remove Perplexity profile (exposed to JavaScript)"""
        try:
            success = account_manager.remove_perplexity_profile(profile_id)
            return {'success': success}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def switchPerplexityProfile(self, profile_id: int) -> Dict:
        """Switch active Perplexity profile (exposed to JavaScript)"""
        try:
            success = account_manager.set_active_perplexity(profile_id)
            return {'success': success}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def getCommitHistory(self, max_count: int = 20) -> list:
        """Get git commit history (exposed to JavaScript as getCommitHistory)"""
        try:
            if sync_engine.git_sync:
                commits = sync_engine.git_sync.get_commit_history(max_count)
                return commits if commits else []
            return []
        except Exception as e:
            logger.error(f"Failed to get commit history: {e}")
            return []
    
    # Window Control Methods
    def minimizeWindow(self):
        """Minimize window (exposed to JavaScript)"""
        try:
            import webview
            windows = webview.windows
            if windows:
                windows[0].minimize()
        except Exception as e:
            logger.error(f"Failed to minimize: {e}")
    
    def maximizeWindow(self):
        """Toggle maximize window (exposed to JavaScript)"""
        try:
            import webview
            windows = webview.windows
            if windows:
                windows[0].toggle_fullscreen()
        except Exception as e:
            logger.error(f"Failed to maximize: {e}")
    
    def closeWindow(self):
        """Close window (exposed to JavaScript)"""
        try:
            import webview
            windows = webview.windows
            if windows:
                windows[0].destroy()
        except Exception as e:
            logger.error(f"Failed to close: {e}")
    
    # Theme Management
    def saveTheme(self, theme_data: Dict) -> Dict:
        """Save custom theme (exposed to JavaScript)"""
        try:
            # Save to config
            config.set('ui.custom_themes', theme_data, save_immediately=True)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def getCustomThemes(self) -> Dict:
        """Get saved custom themes (exposed to JavaScript)"""
        try:
            themes = config.get('ui.custom_themes', {})
            return themes if themes else {}
        except Exception as e:
            return {}

