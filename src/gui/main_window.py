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
    
    def create_perplexity_tab(self, use_custom_account: bool = False):
        """Create a new Perplexity window (native webview window, not iframe)"""
        try:
            # Check max tabs
            if len(self.perplexity_windows) >= config.get('ui.max_tabs', 5):
                return {'success': False, 'message': f'Maximum {config.get("ui.max_tabs", 5)} tabs allowed'}
            
            result = self.tab_manager.create_tab()
            if result['success']:
                tab_info = result['tab']
                tab_id = tab_info['id']
                tab_title = tab_info['title']
                tab_url = tab_info['url']
                
                # Get main window position and size to embed Perplexity window
                main_window_x = 100
                main_window_y = 100
                main_window_width = 1200
                main_window_height = 800
                
                # Get actual window position using Windows API
                if sys.platform == 'win32':
                    try:
                        import ctypes
                        from ctypes import wintypes
                        
                        # Get main window handle
                        user32 = ctypes.windll.user32
                        hwnd = user32.FindWindowW(None, "Wave.AI")
                        
                        if hwnd:
                            # Get window rectangle
                            rect = wintypes.RECT()
                            if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                                main_window_x = rect.left
                                main_window_y = rect.top
                                main_window_width = rect.right - rect.left
                                main_window_height = rect.bottom - rect.top
                    except Exception as e:
                        logger.debug(f"Could not get main window position: {e}")
                
                # Calculate embedded position (sidebar width + padding)
                embedded_x = main_window_x + 50  # Sidebar width
                embedded_y = main_window_y + 82   # Titlebar + toolbar height
                embedded_width = main_window_width - 50  # Full width minus sidebar
                embedded_height = main_window_height - 82  # Full height minus titlebar/toolbar
                
                # Create native webview window (will position after creation)
                perplexity_window = webview.create_window(
                    f'{tab_title} - Wave.AI',
                    tab_url,
                    width=embedded_width,
                    height=embedded_height,
                    resizable=True,
                    min_size=(600, 400),
                    background_color='#ffffff',
                    frameless=True,  # Make it frameless to appear embedded
                    on_top=False
                )
                
                # Position window to appear embedded (Windows API)
                if sys.platform == 'win32':
                    try:
                        import ctypes
                        from ctypes import wintypes
                        
                        # Wait a bit for window to be created
                        import time
                        time.sleep(0.1)
                        
                        # Get window handle
                        windows = webview.windows
                        if len(windows) > 1:  # Main window + this one
                            window_handle = None
                            # Find our window (last one should be the new one)
                            for win in windows:
                                if win != self.main_window:
                                    try:
                                        window_handle = win.native_handle if hasattr(win, 'native_handle') else None
                                        if window_handle:
                                            # Move and resize window
                                            SWP_NOZORDER = 0x0004
                                            ctypes.windll.user32.SetWindowPos(
                                                window_handle,
                                                0,
                                                int(embedded_x),
                                                int(embedded_y),
                                                int(embedded_width),
                                                int(embedded_height),
                                                SWP_NOZORDER
                                            )
                                            logger.info(f"Positioned Perplexity window at ({embedded_x}, {embedded_y})")
                                            break
                                    except Exception as e:
                                        logger.debug(f"Error positioning window: {e}")
                    except Exception as e:
                        logger.debug(f"Could not position window: {e}")
                
                # Store window reference
                window_info = {
                    'window': perplexity_window,
                    'tab_id': tab_id,
                    'title': tab_title,
                    'url': tab_url
                }
                self.perplexity_windows.append(window_info)
                
                logger.info(f"Created Perplexity window: {tab_title} (Tab ID: {tab_id})")
                
                return {
                    'success': True,
                    'tab_id': tab_id,
                    'title': tab_title,
                    'url': tab_url
                }
            return result
        except Exception as e:
            logger.error(f"Failed to create Perplexity window: {e}", exc_info=True)
            return {'success': False, 'message': str(e)}
    
    def close_perplexity_tab(self, tab_id: int):
        """Close a Perplexity window"""
        try:
            # Find and remove the window
            for i, win_info in enumerate(self.perplexity_windows):
                if win_info['tab_id'] == tab_id:
                    try:
                        # Try to destroy the window if it exists
                        win = win_info['window']
                        if win:
                            # Note: pywebview doesn't have a direct destroy method
                            # The window will be closed when the reference is removed
                            pass
                    except Exception as e:
                        logger.debug(f"Error closing window: {e}")
                    
                    # Remove from list
                    removed = self.perplexity_windows.pop(i)
                    
                    # Update tab manager
                    self.tab_manager.close_tab(tab_id)
                    
                    logger.info(f"Closed Perplexity window: {removed['title']}")
                    return {'success': True}
            
            return {'success': False, 'message': 'Window not found'}
        except Exception as e:
            logger.error(f"Failed to close Perplexity window: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_perplexity_tabs(self):
        """Get all Perplexity tabs"""
        return {'success': True, 'tabs': self.tab_manager.get_all_tabs()}
    
    def start(self):
        """Start the GUI application"""
        logger.info("Starting Wave.AI GUI")
        
        # Create tab manager and settings API
        self.tab_manager = PerplexityTabManager()
        self.settings_api = SettingsAPI()
        
        # Add methods for Perplexity tabs
        self.settings_api.create_perplexity_tab = self.create_perplexity_tab
        self.settings_api.close_perplexity_tab = self.close_perplexity_tab
        self.settings_api.get_perplexity_tabs = self.get_perplexity_tabs
        
        # Find and set icon file
        main_dir = Path(__file__).parent.parent.parent
        icon_files = list(main_dir.glob("*.ico"))
        icon_path = str(icon_files[0].absolute()) if icon_files else None
        
        # Create main control window (frameless like Cursor)
        self.main_window = webview.create_window(
            'Wave.AI',
            html=self._get_main_html(),
            js_api=self.settings_api,
            width=1200,
            height=800,
            resizable=True,
            min_size=(800, 600),
            background_color='#0d0d0d',
            frameless=True
        )
        
        # Store icon path for setting after window creation
        self.icon_path = icon_path if (sys.platform == 'win32' and icon_path) else None
        if self.icon_path:
            logger.info(f"Window icon file found: {icon_path}")
        
        # Start webview (this is blocking)
        webview.start(self._on_loaded, debug=False)
    
    def _on_loaded(self):
        """Called when the window is loaded"""
        logger.info("Wave.AI window loaded")
        
        # Set window icon if available (Windows)
        if hasattr(self, 'icon_path') and self.icon_path and sys.platform == 'win32':
            try:
                import ctypes
                from ctypes import wintypes
                import time
                
                # Wait for window to be fully created
                time.sleep(0.2)
                
                # Get window handle from pywebview windows
                windows = webview.windows
                if windows:
                    try:
                        # Try to get handle via native_handle
                        win = windows[0]
                        hwnd = None
                        
                        # Try different methods to get handle
                        if hasattr(win, 'native_handle'):
                            hwnd = win.native_handle
                        elif hasattr(win, 'handle'):
                            hwnd = win.handle
                        else:
                            # Try using FindWindow by title
                            user32 = ctypes.windll.user32
                            hwnd = user32.FindWindowW(None, "Wave.AI")
                        
                        if hwnd:
                            # Load icon from ICO file using shell32
                            icon_path_wide = str(self.icon_path)
                            
                            # Extract icon from ICO file (first icon)
                            icon_handle = ctypes.windll.shell32.ExtractIconW(
                                ctypes.c_void_p(0),
                                icon_path_wide,
                                0
                            )
                            
                            if icon_handle and icon_handle != 1:  # 1 means no icons found
                                try:
                                    # Set window icon using WM_SETICON
                                    WM_SETICON = 0x0080
                                    ICON_SMALL = 0
                                    ICON_BIG = 1
                                    
                                    # Send message to set icon
                                    ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, icon_handle)
                                    ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, icon_handle)
                                    
                                    # Set class icons for taskbar
                                    GCL_HICON = -14
                                    GCL_HICONSM = -34
                                    
                                    # Use SetClassLongPtrW for 64-bit or SetClassLongW for 32-bit
                                    if sys.maxsize > 2**32:
                                        # 64-bit
                                        ctypes.windll.user32.SetClassLongPtrW(hwnd, GCL_HICON, icon_handle)
                                        ctypes.windll.user32.SetClassLongPtrW(hwnd, GCL_HICONSM, icon_handle)
                                    else:
                                        # 32-bit
                                        ctypes.windll.user32.SetClassLongW(hwnd, GCL_HICON, icon_handle)
                                        ctypes.windll.user32.SetClassLongW(hwnd, GCL_HICONSM, icon_handle)
                                    
                                    logger.info(f"Window icon set successfully from {self.icon_path}")
                                except Exception as e:
                                    logger.debug(f"Error setting icon handle: {e}")
                            else:
                                # Fallback: Try LoadImage
                                try:
                                    IMAGE_ICON = 1
                                    LR_LOADFROMFILE = 0x00000010
                                    LR_DEFAULTSIZE = 0x00000040
                                    
                                    icon_handle2 = ctypes.windll.user32.LoadImageW(
                                        0,
                                        icon_path_wide,
                                        IMAGE_ICON,
                                        0,
                                        0,
                                        LR_LOADFROMFILE | LR_DEFAULTSIZE
                                    )
                                    
                                    if icon_handle2:
                                        WM_SETICON = 0x0080
                                        ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 0, icon_handle2)
                                        ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 1, icon_handle2)
                                        logger.info(f"Window icon set using LoadImage from {self.icon_path}")
                                    else:
                                        logger.debug(f"Could not load icon using LoadImage from {self.icon_path}")
                                except Exception as e:
                                    logger.debug(f"Fallback icon loading failed: {e}")
                        else:
                            logger.debug("Could not get window handle for icon")
                    except Exception as e:
                        logger.debug(f"Error setting window icon: {e}")
            except Exception as e:
                logger.debug(f"Could not set window icon: {e}")
        
        # Initialize sync engine in background
        threading.Thread(target=self._init_sync_engine, daemon=True).start()
    
    def _init_sync_engine(self):
        """Initialize sync engine in background (silently, no errors shown)"""
        try:
            if config.is_configured():
                logger.info("Initializing sync engine in background...")
                success, message = sync_engine.initialize()
                if success:
                    logger.info("Sync engine initialized successfully")
                    # Auto-start if configured
                    if config.get('github.auto_pull') or config.get('github.auto_push'):
                        try:
                            sync_engine.start()
                            logger.info("Auto-started sync engine")
                        except Exception as e:
                            logger.debug(f"Could not auto-start sync: {e}")
                else:
                    # Log but don't show error to user on startup
                    logger.debug(f"Background initialization failed (this is normal if not configured): {message}")
        except Exception as e:
            # Silent failure on startup - don't spam user with errors
            logger.debug(f"Background sync initialization error (normal if repo not set up): {e}")
    
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
        
        # Find logo/icon file in main directory for GUI display
        # Use PNG for GUI logo (ICO is for window icon only)
        main_dir = Path(__file__).parent.parent.parent
        logo_files = list(main_dir.glob("*.png")) + list(main_dir.glob("*.jpg")) + list(main_dir.glob("*.svg"))
        
        # Prefer files with "logo" or "icon" in name, or use first PNG found
        logo_path = None
        for f in logo_files:
            name_lower = f.name.lower()
            if 'logo' in name_lower or 'icon' in name_lower or 'new project' in name_lower:
                logo_path = f
                break
        
        if not logo_path and logo_files:
            logo_path = logo_files[0]
        
        if logo_path:
            # Convert to absolute path and normalize for file:// URL (Windows)
            logo_abs_path = logo_path.absolute()
            if sys.platform == 'win32':
                # Windows file:// URL format: file:///C:/path/to/file
                path_str = str(logo_abs_path).replace('\\', '/')
                # Ensure it starts with / for drive letter
                if ':' in path_str and not path_str.startswith('/'):
                    path_str = '/' + path_str
                logo_url = f"file://{path_str}"
            else:
                logo_url = f"file://{logo_abs_path}"
            
            logger.info(f"Logo file found: {logo_path.name}")
            logger.info(f"Logo URL: {logo_url}")
            
            # Alternative: Base64 encode the image for guaranteed loading
            try:
                import base64
                with open(logo_path, 'rb') as img_file:
                    img_data = img_file.read()
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                    # Determine MIME type
                    mime_type = 'image/png'
                    if logo_path.suffix.lower() == '.jpg' or logo_path.suffix.lower() == '.jpeg':
                        mime_type = 'image/jpeg'
                    elif logo_path.suffix.lower() == '.svg':
                        mime_type = 'image/svg+xml'
                    # Use base64 for more reliable loading
                    logo_url = f"data:{mime_type};base64,{img_base64}"
                    logger.info(f"Logo encoded as base64 ({len(img_base64)} chars)")
            except Exception as e:
                logger.warning(f"Could not base64 encode logo, using file:// URL: {e}")
        else:
            logo_url = ""
            logger.warning("No logo file found in main directory")
        
        # Replace placeholders with actual config values
        template = template.replace('REPO_URL_PLACEHOLDER', repo_url)
        template = template.replace('LOCAL_DIR_PLACEHOLDER', local_dir)
        template = template.replace('BRANCH_PLACEHOLDER', branch)
        template = template.replace('LOGO_URL_PLACEHOLDER', logo_url)
        
        # Add JavaScript
        js_code = f"""
        <script>
            // Logo error handler
            function handleLogoError(img) {{
                console.error('Logo image failed to load:', img.src);
                // Don't replace with W, just hide the broken image
                img.style.display = 'none';
                // Try to load via alternative method if possible
            }}
            
            // Try to load logo on page load
            window.addEventListener('load', function() {{
                const logoImg = document.getElementById('logoImage');
                if (logoImg) {{
                    const src = logoImg.src;
                    console.log('Attempting to load logo from:', src);
                    // If it failed, try reloading
                    if (src && src !== 'LOGO_URL_PLACEHOLDER') {{
                        logoImg.onload = function() {{
                            console.log('Logo loaded successfully');
                        }};
                        logoImg.onerror = function() {{
                            console.error('Logo failed to load, trying alternative method');
                            handleLogoError(logoImg);
                        }};
                    }}
                }}
            }});
            
            // Window Controls (for frameless window)
            function minimizeWindow() {{
                if (window.pywebview) {{
                    window.pywebview.api.minimizeWindow();
                }}
            }}
            
            function maximizeWindow() {{
                if (window.pywebview) {{
                    window.pywebview.api.maximizeWindow();
                }}
            }}
            
            function closeWindow() {{
                if (confirm('Close Wave.AI?')) {{
                    if (window.pywebview) {{
                        window.pywebview.api.closeWindow();
                    }}
                }}
            }}
            
            // Theme System
            const themes = {{
                dark: {{
                    bg: '#0d0d0d',
                    cardBg: '#1a1a1a',
                    toolbar: '#1a1a1a',
                    border: '#2a2a2a',
                    text: '#d4d4d4',
                    textMuted: '#9ca3af'
                }},
                light: {{
                    bg: '#ffffff',
                    cardBg: '#f5f5f5',
                    toolbar: '#ffffff',
                    border: '#e5e7eb',
                    text: '#1e1e1e',
                    textMuted: '#6b7280'
                }},
                midnight: {{
                    bg: '#000000',
                    cardBg: '#0a0a0a',
                    toolbar: '#0a0a0a',
                    border: '#1a1a1a',
                    text: '#e0e0e0',
                    textMuted: '#888888'
                }},
                nord: {{
                    bg: '#2e3440',
                    cardBg: '#3b4252',
                    toolbar: '#3b4252',
                    border: '#4c566a',
                    text: '#eceff4',
                    textMuted: '#d8dee9'
                }}
            }};
            
            let currentTheme = 'dark';
            
            function selectTheme(themeName) {{
                currentTheme = themeName;
                document.querySelectorAll('.theme-option').forEach(opt => {{
                    opt.classList.remove('active');
                }});
                const selected = document.querySelector(`[data-theme="${{themeName}}"]`);
                if (selected) selected.classList.add('active');
                
                // Apply immediately when selecting
                applyTheme(themeName);
            }}
            
            function applyTheme(themeName) {{
                try {{
                    const theme = themes[themeName] || themes.dark;
                    if (!theme) return;
                    
                    // Use CSS variables for instant theme switching - much faster than querySelectorAll
                    if (document.documentElement) {{
                        document.documentElement.style.setProperty('--bg-color', theme.bg);
                        document.documentElement.style.setProperty('--card-bg', theme.cardBg);
                        document.documentElement.style.setProperty('--toolbar-bg', theme.toolbar);
                        document.documentElement.style.setProperty('--border-color', theme.border);
                        document.documentElement.style.setProperty('--text-color', theme.text);
                        document.documentElement.style.setProperty('--text-muted', theme.textMuted);
                    }}
                    
                    // Apply to body only
                    if (document.body) {{
                        document.body.style.background = theme.bg;
                        document.body.style.color = theme.text;
                    }}
                }} catch (error) {{
                    console.error('Error applying theme:', error);
                }}
            }}
            
            async function applyCustomTheme() {{
                const applyBtn = event?.target || document.querySelector('[onclick*="applyCustomTheme"]');
                if (applyBtn && applyBtn.disabled) return; // Prevent double-click
                
                try {{
                    if (applyBtn) {{
                        applyBtn.disabled = true;
                        applyBtn.style.opacity = '0.6';
                    }}
                    
                    const customTheme = {{
                        bg: document.getElementById('customBg')?.value || '#0d0d0d',
                        cardBg: document.getElementById('customCardBg')?.value || '#1a1a1a',
                        text: document.getElementById('customText')?.value || '#d4d4d4',
                        accent: document.getElementById('customAccent')?.value || '#667eea',
                        toolbar: document.getElementById('customCardBg')?.value || '#1a1a1a',
                        border: '#2a2a2a',
                        textMuted: '#9ca3af'
                    }};
                    
                    // Use CSS variables for instant theme switching
                    if (document.documentElement) {{
                        document.documentElement.style.setProperty('--bg-color', customTheme.bg);
                        document.documentElement.style.setProperty('--card-bg', customTheme.cardBg);
                        document.documentElement.style.setProperty('--toolbar-bg', customTheme.toolbar);
                        document.documentElement.style.setProperty('--border-color', customTheme.border);
                        document.documentElement.style.setProperty('--text-color', customTheme.text);
                        document.documentElement.style.setProperty('--text-muted', customTheme.textMuted);
                    }}
                    
                    if (document.body) {{
                        document.body.style.background = customTheme.bg;
                        document.body.style.color = customTheme.text;
                    }}
                    
                    // Save to server
                    if (window.pywebview?.api?.saveTheme) {{
                        await window.pywebview.api.saveTheme(customTheme);
                        addToChangelog('System', 'Custom theme applied', '⚙');
                    }}
                }} catch (error) {{
                    console.error('Error applying custom theme:', error);
                    addToChangelog('Error', 'Failed to apply custom theme', '✗');
                }} finally {{
                    if (applyBtn) {{
                        applyBtn.disabled = false;
                        applyBtn.style.opacity = '1';
                    }}
                }}
            }}
            
            // Tab Switching
            function switchTab(tabName) {{
                try {{
                    // Update nav items
                    document.querySelectorAll('.nav-item').forEach(item => {{
                        item.classList.remove('active');
                    }});
                    const navItem = document.querySelector(`[data-tab="${{tabName}}"]`);
                    if (navItem) navItem.classList.add('active');
                    
                    // Update tab content
                    document.querySelectorAll('.tab-content').forEach(tab => {{
                        tab.classList.remove('active');
                    }});
                    const tabContent = document.getElementById(`tab-${{tabName}}`);
                    if (tabContent) tabContent.classList.add('active');
                    
                    // Load data for specific tabs
                    if (tabName === 'commits') {{
                        refreshCommits();
                    }} else if (tabName === 'accounts') {{
                        loadAccountsTab();
                    }} else if (tabName === 'perplexity') {{
                        // Perplexity tab - ensure it's properly displayed
                        // Tabs are managed separately
                    }} else if (tabName === 'activity') {{
                        // Activity log is always updated
                    }}
                }} catch (error) {{
                    console.error('Error switching tab:', error);
                }}
            }}
            
            // Removed expensive button event polling - not needed
            
            // Git Commits
            function refreshCommits() {{
                const commitsList = document.getElementById('commitsList');
                commitsList.innerHTML = '<div class="changelog-item"><div class="changelog-icon">↻</div><div class="changelog-content"><div class="changelog-type">Loading</div><div class="changelog-text">Fetching commits...</div></div></div>';
                
                if (!window.pywebview) return;
                
                window.pywebview.api.getCommitHistory(20).then(commits => {{
                    commitsList.innerHTML = '';
                    
                    if (commits && commits.length > 0) {{
                        commits.forEach(commit => {{
                            const item = document.createElement('div');
                            item.className = 'changelog-item';
                            item.innerHTML = `
                                <div class="changelog-icon">◎</div>
                                <div class="changelog-content">
                                    <div class="changelog-type">${{commit.hash}}</div>
                                    <div class="changelog-text">${{commit.message}}</div>
                                    <div class="changelog-time">${{commit.author}} • ${{commit.date}}</div>
                                </div>
                            `;
                            commitsList.appendChild(item);
                        }});
                    }} else {{
                        commitsList.innerHTML = '<div class="changelog-item"><div class="changelog-icon">○</div><div class="changelog-content"><div class="changelog-type">No commits</div><div class="changelog-text">No commit history available</div></div></div>';
                    }}
                }}).catch(error => {{
                    commitsList.innerHTML = '<div class="changelog-item"><div class="changelog-icon">✗</div><div class="changelog-content"><div class="changelog-type">Error</div><div class="changelog-text">Failed to load commits</div></div></div>';
                }});
            }}
            
            function loadAccountsTab() {{
                // Load accounts in the accounts tab
                const githubSelect2 = document.getElementById('githubAccountSelect2');
                const perplexitySelect2 = document.getElementById('perplexityAccountSelect2');
                
                if (!window.pywebview) return;
                
                window.pywebview.api.getAccounts().then(accounts => {{
                    // GitHub
                    githubSelect2.innerHTML = '<option value="">Select GitHub Account...</option>';
                    accounts.github_accounts.forEach(acc => {{
                        const option = document.createElement('option');
                        option.value = acc.id;
                        option.textContent = `${{acc.username}} - ${{acc.repo_url}}`;
                        if (acc.id === accounts.active_github) option.selected = true;
                        githubSelect2.appendChild(option);
                    }});
                    
                    // Perplexity
                    perplexitySelect2.innerHTML = '<option value="">Select Perplexity Profile...</option>';
                    accounts.perplexity_profiles.forEach(prof => {{
                        const option = document.createElement('option');
                        option.value = prof.id;
                        option.textContent = prof.name;
                        if (prof.id === accounts.active_perplexity) option.selected = true;
                        perplexitySelect2.appendChild(option);
                    }});
                }});
            }}
            
            // Account Management
            function loadAccounts() {{
                if (!window.pywebview) return;
                
                window.pywebview.api.getAccounts().then(accounts => {{
                    // Load GitHub accounts
                    const githubSelect = document.getElementById('githubAccountSelect');
                    githubSelect.innerHTML = '<option value="">Select GitHub Account...</option>';
                    accounts.github_accounts.forEach(acc => {{
                        const option = document.createElement('option');
                        option.value = acc.id;
                        option.textContent = `${{acc.username}} - ${{acc.repo_url}}`;
                        if (acc.id === accounts.active_github) {{
                            option.selected = true;
                        }}
                        githubSelect.appendChild(option);
                    }});
                    
                    // Load Perplexity profiles
                    const perplexitySelect = document.getElementById('perplexityAccountSelect');
                    perplexitySelect.innerHTML = '<option value="">Select Perplexity Profile...</option>';
                    accounts.perplexity_profiles.forEach(prof => {{
                        const option = document.createElement('option');
                        option.value = prof.id;
                        option.textContent = prof.name;
                        if (prof.id === accounts.active_perplexity) {{
                            option.selected = true;
                        }}
                        perplexitySelect.appendChild(option);
                    }});
                }});
            }}
            
            function switchGithubAccount() {{
                const select = document.getElementById('githubAccountSelect');
                const accountId = parseInt(select.value);
                if (accountId) {{
                    window.pywebview.api.switchGithubAccount(accountId).then(result => {{
                        if (result.success) {{
                            addToChangelog('Account', `Switched to GitHub: ${{select.options[select.selectedIndex].text}}`, '⚙');
                            updateStatus();
                        }}
                    }});
                }}
            }}
            
            function switchPerplexityAccount() {{
                const select = document.getElementById('perplexityAccountSelect');
                const profileId = parseInt(select.value);
                if (profileId) {{
                    window.pywebview.api.switchPerplexityProfile(profileId).then(result => {{
                        if (result.success) {{
                            addToChangelog('Account', `Switched to profile: ${{select.options[select.selectedIndex].text}}`, '⚙');
                        }}
                    }});
                }}
            }}
            
            function addGithubAccount() {{
                const username = prompt('GitHub username:');
                if (!username) return;
                const repoUrl = prompt('Repository URL:');
                if (!repoUrl) return;
                const localDir = prompt('Local directory:');
                if (!localDir) return;
                
                window.pywebview.api.addGithubAccount(username, repoUrl, localDir).then(result => {{
                    if (result.success) {{
                        addToChangelog('Account', `Added GitHub account: ${{username}}`, '+');
                        loadAccounts();
                    }} else {{
                        alert('Failed to add account');
                    }}
                }});
            }}
            
            function addPerplexityAccount() {{
                const name = prompt('Profile name:');
                if (!name) return;
                const notes = prompt('Notes (optional):') || '';
                
                window.pywebview.api.addPerplexityProfile(name, notes).then(result => {{
                    if (result.success) {{
                        addToChangelog('Account', `Added Perplexity profile: ${{name}}`, '+');
                        loadAccounts();
                    }} else {{
                        alert('Failed to add profile');
                    }}
                }});
            }}
            
            function removeGithubAccount() {{
                const select = document.getElementById('githubAccountSelect');
                const accountId = parseInt(select.value);
                if (!accountId) {{
                    alert('Please select an account to remove');
                    return;
                }}
                if (confirm('Remove this GitHub account?')) {{
                    window.pywebview.api.removeGithubAccount(accountId).then(result => {{
                        if (result.success) {{
                            addToChangelog('Account', 'GitHub account removed', '-');
                            loadAccounts();
                        }}
                    }});
                }}
            }}
            
            function removePerplexityAccount() {{
                const select = document.getElementById('perplexityAccountSelect');
                const profileId = parseInt(select.value);
                if (!profileId) {{
                    alert('Please select a profile to remove');
                    return;
                }}
                if (confirm('Remove this Perplexity profile?')) {{
                    window.pywebview.api.removePerplexityProfile(profileId).then(result => {{
                        if (result.success) {{
                            addToChangelog('Account', 'Perplexity profile removed', '-');
                            loadAccounts();
                        }}
                    }});
                }}
            }}
            
            // Changelog management
            let changelogItems = [];
            const maxChangelogItems = 5;
            
            function addToChangelog(type, text, icon = '○') {{
                try {{
                    const changelogList = document.getElementById('changelogList');
                    if (!changelogList) {{
                        console.warn('Changelog list not found');
                        return;
                    }}
                    
                    const now = new Date();
                    const timeStr = now.toLocaleTimeString('en-US', {{ hour: '2-digit', minute: '2-digit' }});
                    
                    const item = document.createElement('div');
                    item.className = 'changelog-item';
                    item.style.opacity = '0';
                    item.style.transform = 'translateX(-20px)';
                    item.innerHTML = `
                        <div class="changelog-icon">${{icon}}</div>
                        <div class="changelog-content">
                            <div class="changelog-type">${{type}}</div>
                            <div class="changelog-text">${{text}}</div>
                            <div class="changelog-time">${{timeStr}}</div>
                        </div>
                    `;
                    
                    if (changelogList.firstChild) {{
                        changelogList.insertBefore(item, changelogList.firstChild);
                    }} else {{
                        changelogList.appendChild(item);
                    }}
                    
                    // Animate in
                    setTimeout(() => {{
                        if (item && item.style) {{
                            item.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
                            item.style.opacity = '1';
                            item.style.transform = 'translateX(0)';
                        }}
                    }}, 10);
                    
                    // Keep only last 5 items
                    while (changelogList && changelogList.children && changelogList.children.length > maxChangelogItems) {{
                        const lastItem = changelogList.lastChild;
                        if (lastItem && lastItem.style) {{
                            lastItem.style.opacity = '0';
                            lastItem.style.transform = 'translateX(20px)';
                            setTimeout(() => {{
                                if (lastItem && lastItem.parentNode) {{
                                    lastItem.remove();
                                }}
                            }}, 400);
                        }} else {{
                            // If lastItem is null, just remove it
                            if (lastItem) {{
                                lastItem.remove();
                            }} else {{
                                break;
                            }}
                        }}
                    }}
                }} catch (error) {{
                    console.error('Error adding to changelog:', error);
                    // Don't throw - just log the error so GUI doesn't break
                }}
            }}
            
            // Perplexity Tab Management
            let customAccountEnabled = false;
            let activePerplexityTabId = null;
            
            function toggleCustomAccount() {{
                customAccountEnabled = !customAccountEnabled;
                const toggle = document.getElementById('accountToggle');
                const toggleSwitch = document.getElementById('accountToggleSwitch');
                if (customAccountEnabled) {{
                    toggle.classList.add('active');
                    toggleSwitch.classList.add('active');
                }} else {{
                    toggle.classList.remove('active');
                    toggleSwitch.classList.remove('active');
                }}
            }}
            
            async function createPerplexityTab() {{
                if (!window.pywebview || !window.pywebview.api) return;
                
                // Switch to Perplexity tab if not already there
                switchTab('perplexity');
                
                addToChangelog('Action', 'Opening new Perplexity window...', '+');
                try {{
                    const result = await window.pywebview.api.create_perplexity_tab(customAccountEnabled);
                    if (result && result.success) {{
                        const tabId = result.tab_id;
                        const tabTitle = result.title || `Perplexity ${{tabId + 1}}`;
                        
                        // Create tab header to show in UI (window opens separately)
                        createPerplexityTabHeader(tabId, tabTitle);
                        
                        // Ensure we're on the Perplexity tab
                        const perplexityTab = document.getElementById('tab-perplexity');
                        if (perplexityTab && !perplexityTab.classList.contains('active')) {{
                            switchTab('perplexity');
                        }}
                        
                        // Show message that window opened
                        showPerplexityWindowMessage(tabId, tabTitle);
                        
                        addToChangelog('Success', `Perplexity window "${{tabTitle}}" opened`, '✓');
                    }} else {{
                        const msg = result.message || 'Unknown error';
                        alert('⚠ ' + msg);
                        addToChangelog('Warning', msg, '⚠');
                    }}
                }} catch (error) {{
                    console.error('Create tab error:', error);
                    alert('✗ Failed to open Perplexity window: ' + (error.message || error));
                    addToChangelog('Error', 'Failed to open window', '✗');
                }}
            }}
            
            function showPerplexityWindowMessage(tabId, title) {{
                const container = document.getElementById('perplexityFramesContainer');
                if (!container) return;
                
                // Hide the container content - window is positioned over it
                container.style.display = 'none';
                
                // Note: The Perplexity window is positioned to appear embedded
                // in the main window, covering the tab content area
            }}
            
            function createPerplexityTabHeader(tabId, title) {{
                const tabsList = document.getElementById('perplexityTabsList');
                
                const tabItem = document.createElement('div');
                tabItem.className = 'perplexity-tab-item';
                tabItem.id = `perplexityTabHeader_${{tabId}}`;
                tabItem.onclick = (e) => {{
                    if (e.target.classList.contains('perplexity-tab-close')) return;
                    switchPerplexityTab(tabId);
                }};
                
                tabItem.innerHTML = `
                    <span>${{title}}</span>
                    <div class="perplexity-tab-close" onclick="closePerplexityTab(${{tabId}}, event)">×</div>
                `;
                
                tabsList.appendChild(tabItem);
            }}
            
            function switchPerplexityTab(tabId) {{
                console.log('Switching to Perplexity tab', tabId);
                
                // Remove active class from all tab headers
                document.querySelectorAll('.perplexity-tab-item').forEach(item => {{
                    item.classList.remove('active');
                }});
                
                // Activate tab header
                const tabHeader = document.getElementById(`perplexityTabHeader_${{tabId}}`);
                if (tabHeader) {{
                    tabHeader.classList.add('active');
                }}
                
                // Hide container - the window is positioned over it
                const container = document.getElementById('perplexityFramesContainer');
                if (container) {{
                    container.style.display = 'none';
                }}
                
                activePerplexityTabId = tabId;
            }}
            
            async function closePerplexityTab(tabId, event) {{
                if (event) event.stopPropagation();
                
                if (!window.pywebview || !window.pywebview.api) return;
                
                try {{
                    const result = await window.pywebview.api.close_perplexity_tab(tabId);
                    if (result && result.success) {{
                        // Remove message
                        const message = document.getElementById(`perplexityMsg_${{tabId}}`);
                        if (message) message.remove();
                        
                        // Remove tab header
                        const tabHeader = document.getElementById(`perplexityTabHeader_${{tabId}}`);
                        if (tabHeader) tabHeader.remove();
                        
                        // Switch to another tab if this was active
                        if (activePerplexityTabId === tabId) {{
                            const remainingTabs = document.querySelectorAll('.perplexity-tab-item');
                            if (remainingTabs.length > 0) {{
                                const firstTab = remainingTabs[0];
                                const firstTabId = parseInt(firstTab.id.split('_')[1]);
                                switchPerplexityTab(firstTabId);
                            }} else {{
                                // Show empty state
                                const container = document.getElementById('perplexityFramesContainer');
                                container.style.display = 'flex';
                                container.innerHTML = `
                                    <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #6b7280; flex-direction: column; gap: 12px; width: 100%;">
                                        <div style="font-size: 48px;">◐</div>
                                        <div style="font-size: 16px; font-weight: 500;">No Perplexity windows open</div>
                                        <div style="font-size: 13px;">Click "New Tab" to open a new Perplexity window</div>
                                    </div>
                                `;
                            }}
                        }}
                        
                        addToChangelog('Action', `Perplexity window ${{tabId + 1}} closed`, '✗');
                    }} else {{
                        alert('Cannot close the last window');
                    }}
                }} catch (error) {{
                    console.error('Close tab error:', error);
                    alert('Failed to close tab: ' + (error.message || error));
                }}
            }}
            
            async function manualSync() {{
                if (!window.pywebview) return;
                
                addToChangelog('Sync', 'Manual sync initiated...', '↻');
                try {{
                    const result = await window.pywebview.api.manual_sync();
                    if (result.success) {{
                        alert('✓ Manual sync completed!');
                        addToChangelog('Success', 'Manual sync completed', '✓');
                        await updateStatus();
                    }} else {{
                        alert('✗ Manual sync failed: ' + result.message);
                        addToChangelog('Error', 'Manual sync failed', '✗');
                    }}
                }} catch (error) {{
                    console.error('Manual sync error:', error);
                    addToChangelog('Error', 'Manual sync failed', '✗');
                }}
            }}
            
            async function startSync() {{
                if (!window.pywebview || !window.pywebview.api) {{
                    alert('✗ Error: Wave.AI API not ready. Please wait a moment and try again.');
                    addToChangelog('Error', 'API not ready', '✗');
                    return;
                }}
                
                addToChangelog('Sync', 'Starting automatic sync...', '▶');
                
                // Disable button to prevent multiple clicks
                let startBtn = null;
                try {{
                    // Try to find the start sync button
                    const buttons = document.querySelectorAll('.btn');
                    for (let btn of buttons) {{
                        if (btn.textContent && btn.textContent.includes('Start Sync')) {{
                            startBtn = btn;
                            btn.disabled = true;
                            btn.style.opacity = '0.6';
                            btn.style.pointerEvents = 'none';
                            break;
                        }}
                    }}
                }} catch (e) {{
                    console.debug('Could not disable button:', e);
                }}
                
                try {{
                    // Check if method exists
                    if (typeof window.pywebview.api.start_sync !== 'function') {{
                        throw new Error('start_sync method not available on API');
                    }}
                    
                    // Call API - this returns immediately now (initialization in background)
                    const result = await window.pywebview.api.start_sync();
                    console.log('Start sync result:', result);
                    
                    if (result && result.success) {{
                        if (result.message && result.message.includes('background')) {{
                            addToChangelog('Sync', 'Sync engine initializing in background...', '⏳');
                        }} else {{
                            addToChangelog('Success', 'Automatic sync started', '✓');
                        }}
                        // Update status after a delay to let initialization complete
                        setTimeout(async () => {{
                            await updateStatus();
                        }}, 2000);
                    }} else {{
                        const errorMsg = result && result.message ? result.message : 'Unknown error';
                        alert('✗ Failed to start sync:\\n\\n' + errorMsg + '\\n\\nPlease check:\\n1. Repository URL is set\\n2. Local directory exists\\n3. Git is configured');
                        addToChangelog('Error', 'Failed to start sync: ' + errorMsg, '✗');
                    }}
                }} catch (error) {{
                    const errorMsg = error.message || error.toString() || 'Unknown error';
                    console.error('Start sync error:', error);
                    alert('✗ Error starting sync:\\n\\n' + errorMsg + '\\n\\nPlease check your configuration in Settings.');
                    addToChangelog('Error', 'Failed to start sync: ' + errorMsg, '✗');
                }} finally {{
                    // Re-enable button after a delay
                    setTimeout(() => {{
                        if (startBtn) {{
                            startBtn.disabled = false;
                            startBtn.style.opacity = '1';
                            startBtn.style.pointerEvents = 'auto';
                        }}
                    }}, 1000);
                }}
            }}
            
            async function stopSync() {{
                if (!window.pywebview || !window.pywebview.api) {{
                    alert('✗ Error: Wave.AI API not ready.');
                    addToChangelog('Error', 'API not ready', '✗');
                    return;
                }}
                
                addToChangelog('Sync', 'Stopping automatic sync...', '⏸');
                try {{
                    const result = await window.pywebview.api.stop_sync();
                    console.log('Stop sync result:', result);
                    
                    if (result && result.success) {{
                        addToChangelog('Success', 'Automatic sync stopped', '✓');
                        await updateStatus();
                    }} else {{
                        const errorMsg = result && result.message ? result.message : 'Unknown error';
                        alert('✗ Failed to stop sync:\\n\\n' + errorMsg);
                        addToChangelog('Error', 'Failed to stop sync: ' + errorMsg, '✗');
                    }}
                }} catch (error) {{
                    const errorMsg = error.message || error.toString() || 'Unknown error';
                    console.error('Stop sync error:', error);
                    alert('✗ Error stopping sync:\\n\\n' + errorMsg);
                    addToChangelog('Error', 'Failed to stop sync: ' + errorMsg, '✗');
                }}
            }}
            
            async function updateStatus() {{
                const dot = document.getElementById('statusDot');
                const text = document.getElementById('statusText');
                const syncStatus = document.getElementById('syncStatus');
                const repoUrl = document.getElementById('repoUrl');
                const localDir = document.getElementById('localDir');
                const branchName = document.getElementById('branchName');
                
                if (!window.pywebview || !window.pywebview.api) {{
                    // pywebview not ready yet
                    if (dot) {{
                        dot.classList.add('idle');
                        dot.style.background = '#6b7280';
                    }}
                    if (text) text.textContent = 'Loading...';
                    if (syncStatus) syncStatus.textContent = 'Initializing...';
                    return;
                }}
                
                try {{
                    const status = await window.pywebview.api.get_status();
                    
                    console.log('Status received:', status);  // Debug
                    
                    // Update top-right status pill
                    if (dot && text) {{
                        if (status.is_running === true) {{
                            dot.classList.remove('idle');
                            dot.style.background = '#10b981'; // Green
                            text.textContent = 'Syncing';
                        }} else {{
                            dot.classList.add('idle');
                            dot.style.background = '#6b7280'; // Gray
                            text.textContent = 'Ready';
                        }}
                    }}
                    
                    // Update sync status card
                    if (syncStatus) {{
                        if (status.is_running === true) {{
                            const interval = (status.config && status.config.sync_interval) ? status.config.sync_interval : 30;
                            syncStatus.textContent = 'Active - Syncing every ' + interval + 's';
                            syncStatus.className = 'card-value active';
                        }} else {{
                            syncStatus.textContent = 'Stopped - Click Start Sync';
                            syncStatus.className = 'card-value inactive';
                        }}
                    }}
                    
                    // Update repository info
                    if (status.config) {{
                        if (repoUrl && status.config.repo_url) {{
                            repoUrl.textContent = status.config.repo_url;
                        }}
                        if (localDir && status.config.local_dir) {{
                            localDir.textContent = status.config.local_dir;
                        }}
                    }}
                    
                    // Update branch
                    if (branchName) {{
                        if (status.git_status && status.git_status.current_branch) {{
                            branchName.textContent = status.git_status.current_branch;
                        }} else {{
                            branchName.textContent = status.config && status.config.branch ? status.config.branch : 'main';
                        }}
                    }}
                    
                }} catch (error) {{
                    console.error('Status update failed:', error);
                    if (dot) {{
                        dot.classList.add('idle');
                        dot.style.background = '#ef4444'; // Red for error
                    }}
                    if (text) text.textContent = 'Error';
                    if (syncStatus) syncStatus.textContent = 'Failed to get status';
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
                        
                        // Load theme
                        const savedTheme = settings.ui.theme || 'dark';
                        selectTheme(savedTheme);
                    }});
                }}
            }}
            
            async function saveSettings() {{
                if (!window.pywebview) return;
                
                const settings = {{
                    repo_url: document.getElementById('settingsRepoUrl').value,
                    localDir: document.getElementById('settingsLocalDir').value,
                    branch: document.getElementById('settingsBranch').value,
                    sync_interval: parseInt(document.getElementById('settingsSyncInterval').value),
                    theme: currentTheme
                }};
                
                addToChangelog('Settings', 'Saving configuration...', '⚙');
                
                try {{
                    const result = await window.pywebview.api.save_settings(settings);
                    if (result.success) {{
                        alert('✓ Settings saved successfully!');
                        addToChangelog('Success', 'Settings updated', '✓');
                        applyTheme(currentTheme);
                        closeSettings();
                        await updateStatus();
                    }} else {{
                        alert('✗ Failed to save settings: ' + result.message);
                        addToChangelog('Error', 'Failed to save settings', '✗');
                    }}
                }} catch (error) {{
                    console.error('Save settings error:', error);
                    addToChangelog('Error', 'Failed to save settings', '✗');
                }}
            }}
            
            // Update status only on demand (when actions are taken)
            // No more expensive polling - status updates happen after user actions
            
            // Check for pywebview availability repeatedly
            let pywebviewReady = false;
            const checkPywebview = setInterval(() => {{
                if (window.pywebview && window.pywebview.api && !pywebviewReady) {{
                    pywebviewReady = true;
                    clearInterval(checkPywebview);
                    
                    // Now initialize everything
                    initializeApp();
                }}
            }}, 100);
            
            async function initializeApp() {{
                console.log('Initializing Wave.AI...');
                
                // Debug: Log all available API methods
                if (window.pywebview && window.pywebview.api) {{
                    const apiMethods = Object.getOwnPropertyNames(window.pywebview.api).filter(
                        name => typeof window.pywebview.api[name] === 'function'
                    );
                    console.log('Available API methods:', apiMethods);
                    console.log('start_sync type:', typeof window.pywebview.api.start_sync);
                }}
                
                // Load theme first
                try {{
                    const settings = await window.pywebview.api.get_settings();
                    const savedTheme = settings.ui && settings.ui.theme ? settings.ui.theme : 'dark';
                    currentTheme = savedTheme;
                    
                    console.log('Loading saved theme:', savedTheme);
                    
                    // Select theme option
                    document.querySelectorAll('.theme-option').forEach(opt => {{
                        opt.classList.remove('active');
                    }});
                    const themeOption = document.querySelector(`[data-theme="${{savedTheme}}"]`);
                    if (themeOption) {{
                        themeOption.classList.add('active');
                    }}
                    
                    // Apply theme
                    applyTheme(savedTheme);
                    
                }} catch (error) {{
                    console.error('Theme load error:', error);
                    // Fallback to dark theme
                    applyTheme('dark');
                }}
                
                // Update status
                await updateStatus();
                
                // Load accounts
                loadAccounts();
                
                // Add to changelog
                addToChangelog('System', 'Wave.AI ready', '✓');
                
                console.log('Wave.AI initialized successfully');
            }}
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

