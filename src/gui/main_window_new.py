"""
Main Window for Wave.AI GUI
Clean, modern Cursor-like interface with Perplexity webview and controls
"""

import webview
import threading
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.core.sync_engine import sync_engine
from src.core.config_manager import config
from src.gui.perplexity_tabs import PerplexityTabManager
from src.gui.settings_panel import SettingsAPI
from src.utils.logger import logger


class WaveAI:
    """Main Wave.AI application"""
    
    def __init__(self):
        self.tab_manager = None
        self.main_window = None
        self.perplexity_windows = []
        self.settings_window = None
        self.is_initialized = False
        self.settings_api = None
    
    def create_perplexity_tab(self):
        """Create a new Perplexity tab window"""
        if len(self.perplexity_windows) >= config.get('ui.max_tabs', 5):
            logger.warning("Maximum tabs reached")
            return {'success': False, 'message': 'Maximum tabs reached'}
        
        tab_num = len(self.perplexity_windows) + 1
        perplexity_url = config.get('perplexity.url', 'https://www.perplexity.ai')
        
        # Create new window for Perplexity
        perplexity_window = webview.create_window(
            f'Perplexity {tab_num} - Wave.AI',
            perplexity_url,
            width=1200,
            height=800,
            resizable=True,
            on_top=False
        )
        
        self.perplexity_windows.append(perplexity_window)
        logger.info(f"Created Perplexity tab {tab_num}")
        
        return {'success': True, 'tab_number': tab_num}
    
    def start(self):
        """Start the GUI application"""
        logger.info("Starting Wave.AI GUI")
        
        # Create tab manager and settings API
        self.tab_manager = PerplexityTabManager()
        self.settings_api = SettingsAPI()
        
        # Add method to create Perplexity tabs
        self.settings_api.createPerplexityTab = self.create_perplexity_tab
        
        # Create main control window
        self.main_window = webview.create_window(
            'Wave.AI',
            html=self._get_main_html(),
            js_api=self.settings_api,
            width=900,
            height=700,
            resizable=True,
            background_color='#0d0d0d'
        )
        
        # Start webview (this is blocking)
        webview.start(self._on_loaded, debug=False)
    
    def _on_loaded(self):
        """Called when the window is loaded"""
        logger.info("Wave.AI window loaded")
        
        # Initialize sync engine in background
        threading.Thread(target=self._init_sync_engine, daemon=True).start()
    
    def _init_sync_engine(self):
        """Initialize sync engine"""
        if config.is_configured():
            logger.info("Initializing sync engine...")
            success, message = sync_engine.initialize()
            if success:
                logger.info("Sync engine initialized successfully")
                # Auto-start if configured
                if config.get('github.auto_pull') or config.get('github.auto_push'):
                    sync_engine.start()
            else:
                logger.error(f"Failed to initialize sync engine: {message}")
    
    def _get_main_html(self) -> str:
        """Generate main HTML interface"""
        # Get config values for display
        repo_url = config.get('github.repo_url', 'Not configured')
        local_dir = config.get('local.code_directory', 'Not configured')
        branch = config.get('github.branch', 'main')
        sync_interval = config.get('github.sync_interval', 30)
        
        html_content = Path(__file__).parent / "modern_ui.html"
        if html_content.exists():
            with open(html_content, 'r', encoding='utf-8') as f:
                template = f.read()
        else:
            # Fallback inline HTML if file doesn't exist
            template = self._get_inline_html()
        
        # Replace placeholders with actual config values
        template = template.replace('REPO_URL_PLACEHOLDER', repo_url)
        template = template.replace('LOCAL_DIR_PLACEHOLDER', local_dir)
        template = template.replace('BRANCH_PLACEHOLDER', branch)
        
        # Add JavaScript
        js_code = f"""
        <script>
            function createPerplexityTab() {{
                if (window.pywebview) {{
                    window.pywebview.api.createPerplexityTab().then(result => {{
                        if (result && result.success) {{
                            updateStatus();
                        }} else {{
                            alert('⚠ Maximum tabs reached (5 tabs allowed)');
                        }}
                    }});
                }}
            }}
            
            function manualSync() {{
                if (window.pywebview) {{
                    window.pywebview.api.manual_sync().then(result => {{
                        if (result.success) {{
                            alert('✓ Manual sync completed!');
                            updateStatus();
                        }} else {{
                            alert('✗ Manual sync failed: ' + result.message);
                        }}
                    }});
                }}
            }}
            
            function startSync() {{
                if (window.pywebview) {{
                    window.pywebview.api.startSync().then(result => {{
                        if (result.success) {{
                            alert('✓ Sync started successfully!');
                            updateStatus();
                        }} else {{
                            alert('✗ Failed to start sync: ' + result.message);
                        }}
                    }});
                }}
            }}
            
            function stopSync() {{
                if (window.pywebview) {{
                    window.pywebview.api.stopSync().then(result => {{
                        if (result.success) {{
                            alert('✓ Sync stopped');
                            updateStatus();
                        }} else {{
                            alert('✗ Failed to stop sync: ' + result.message);
                        }}
                    }});
                }}
            }}
            
            function updateStatus() {{
                if (window.pywebview) {{
                    window.pywebview.api.getStatus().then(status => {{
                        const dot = document.getElementById('statusDot');
                        const text = document.getElementById('statusText');
                        const syncStatus = document.getElementById('syncStatus');
                        const repoUrl = document.getElementById('repoUrl');
                        const localDir = document.getElementById('localDir');
                        const branchName = document.getElementById('branchName');
                        
                        if (status.is_running) {{
                            dot.classList.remove('idle');
                            text.textContent = 'Running';
                            syncStatus.textContent = 'Active';
                            syncStatus.classList.add('active');
                            syncStatus.classList.remove('inactive');
                        }} else {{
                            dot.classList.add('idle');
                            text.textContent = 'Idle';
                            syncStatus.textContent = 'Stopped';
                            syncStatus.classList.add('inactive');
                            syncStatus.classList.remove('active');
                        }}
                        
                        if (status.config) {{
                            if (status.config.repo_url) {{
                                repoUrl.textContent = status.config.repo_url;
                            }}
                            if (status.config.local_dir) {{
                                localDir.textContent = status.config.local_dir;
                            }}
                        }}
                        
                        // Update branch if available
                        if (status.git_status && status.git_status.current_branch) {{
                            branchName.textContent = status.git_status.current_branch;
                        }}
                    }});
                }}
            }}
            
            function openSettings() {{
                document.getElementById('settingsPanel').classList.add('open');
                loadSettings();
            }}
            
            function closeSettings() {{
                document.getElementById('settingsPanel').classList.remove('open');
            }}
            
            function loadSettings() {{
                if (window.pywebview) {{
                    window.pywebview.api.get_settings().then(settings => {{
                        document.getElementById('settingsRepoUrl').value = settings.github.repo_url || '';
                        document.getElementById('settingsLocalDir').value = settings.local.code_directory || '';
                        document.getElementById('settingsBranch').value = settings.github.branch || 'main';
                        document.getElementById('settingsSyncInterval').value = settings.github.sync_interval || 30;
                    }});
                }}
            }}
            
            function saveSettings() {{
                if (window.pywebview) {{
                    const settings = {{
                        repo_url: document.getElementById('settingsRepoUrl').value,
                        localDir: document.getElementById('settingsLocalDir').value,
                        branch: document.getElementById('settingsBranch').value,
                        sync_interval: parseInt(document.getElementById('settingsSyncInterval').value)
                    }};
                    
                    window.pywebview.api.saveSettings(settings).then(result => {{
                        if (result.success) {{
                            alert('✓ Settings saved successfully!');
                            closeSettings();
                            updateStatus();
                        }} else {{
                            alert('✗ Failed to save settings: ' + result.message);
                        }}
                    }});
                }}
            }}
            
            // Update status every 5 seconds
            setInterval(() => {{
                updateStatus();
            }}, 5000);
            
            // Initial status update
            setTimeout(() => {{
                updateStatus();
            }}, 1000);
        </script>
        """
        
        # Insert JavaScript before closing body tag
        template = template.replace('// JavaScript functions will be added here', '')
        template = template.replace('</body>', js_code + '</body>')
        
        return template
    
    def _get_inline_html(self):
        """Fallback inline HTML if template file doesn't exist"""
        return """<!DOCTYPE html>
<html>
<head><title>Wave.AI</title></head>
<body style="background: #0d0d0d; color: #d4d4d4; font-family: sans-serif; padding: 40px; text-align: center;">
    <h1>Wave.AI</h1>
    <p>Modern UI template not found. Using fallback.</p>
    <div id="repoUrl"></div>
    <div id="localDir"></div>
    <div id="syncStatus"></div>
    <div id="branchName"></div>
    <div id="statusDot"></div>
    <div id="statusText"></div>
    <div id="settingsPanel"></div>
</body>
</html>"""


def start_gui():
    """Start the Wave.AI GUI"""
    app = WaveAI()
    app.start()


if __name__ == '__main__':
    start_gui()

