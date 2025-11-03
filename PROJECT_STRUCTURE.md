# 📁 Wave.AI Project Structure

Complete overview of the codebase organization.

```
Wave.AI/
│
├── 📄 main.py                      # Main entry point (GUI/CLI launcher)
├── 📄 wave-ai.py                   # CLI wrapper script
├── 📄 setup.py                     # Installation script
├── 📄 requirements.txt             # Python dependencies
│
├── 📖 Documentation/
│   ├── README.md                   # Main user guide
│   ├── ARCHITECTURE.md             # System design & data flow
│   ├── SETUP_GUIDE.md              # Detailed setup instructions
│   ├── QUICKSTART.md               # 5-minute quick start
│   ├── TROUBLESHOOTING.md          # Common issues & solutions
│   ├── PROJECT_STRUCTURE.md        # This file
│   └── LICENSE                     # MIT License
│
├── 🔧 Configuration/
│   └── config/
│       ├── settings.json           # User configuration (created on first run)
│       └── settings.template.json  # Template configuration
│
├── 📝 Logs/
│   └── logs/
│       ├── wave_YYYYMMDD.log       # Daily application logs
│       └── version_history.json    # Version control checkpoints
│
├── 💻 Source Code/
│   └── src/
│       ├── __init__.py
│       │
│       ├── 🔄 Core Modules/
│       │   ├── core/
│       │   │   ├── __init__.py
│       │   │   ├── config_manager.py       # Configuration handling
│       │   │   ├── git_sync.py             # Git operations (pull/push/commit)
│       │   │   ├── version_control.py      # Revert/forward functionality
│       │   │   ├── file_watcher.py         # File system monitoring
│       │   │   └── sync_engine.py          # Main sync coordinator
│       │   │
│       │   ├── 🖥️ GUI Modules/
│       │   │   ├── gui/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── main_window.py      # Main GUI window
│       │   │   │   ├── perplexity_tabs.py  # Multi-tab manager
│       │   │   │   └── settings_panel.py   # Settings API
│       │   │
│       │   ├── 💬 CLI Modules/
│       │   │   ├── cli/
│       │   │   │   ├── __init__.py
│       │   │   │   └── commands.py         # CLI commands implementation
│       │   │
│       │   └── 🛠️ Utilities/
│       │       └── utils/
│       │           ├── __init__.py
│       │           ├── logger.py           # Logging system
│       │           ├── prompt_templates.py # Perplexity prompts
│       │           └── conflict_handler.py # Merge conflict resolution
│
└── 🪟 Windows Launchers/
    ├── Wave.AI.bat                 # GUI launcher (created by setup)
    └── Wave.AI-CLI.bat             # CLI launcher (created by setup)
```

---

## 📂 Module Descriptions

### Core Modules (`src/core/`)

#### `config_manager.py`
- Loads and saves configuration
- Validates settings
- Provides default values
- JSON-based configuration

**Key Classes:**
- `ConfigManager` - Main configuration handler

**Usage:**
```python
from src.core.config_manager import config
repo_url = config.get('github.repo_url')
config.set('github.branch', 'main')
```

#### `git_sync.py`
- Git operations wrapper
- Pull, push, commit, status
- Conflict detection
- Remote change checking

**Key Classes:**
- `GitSync` - Git operations handler

**Key Methods:**
- `pull()` - Pull from remote
- `push()` - Push to remote
- `commit()` - Create commit
- `commit_and_push()` - Combined operation
- `has_remote_changes()` - Check for updates
- `get_status()` - Repository status

#### `version_control.py`
- Checkpoint management
- Revert/forward navigation
- History tracking
- Version search

**Key Classes:**
- `VersionControl` - Version management

**Key Methods:**
- `create_checkpoint()` - Save current state
- `revert()` - Go back N steps
- `forward()` - Go forward N steps
- `goto_checkpoint()` - Jump to specific version
- `get_history_summary()` - View history

#### `file_watcher.py`
- Monitors local directory
- Detects file changes
- Debounce mechanism
- Pattern-based filtering

**Key Classes:**
- `FileWatcher` - File system monitor
- `ChangeHandler` - Event handler

**Key Methods:**
- `start()` - Begin watching
- `stop()` - Stop watching
- `pause()` / `resume()` - Temporary pause
- `set_change_callback()` - Set callback function

#### `sync_engine.py`
- Orchestrates all components
- Auto-sync loop
- Conflict handling
- Status management

**Key Classes:**
- `SyncEngine` - Main coordinator

**Key Methods:**
- `initialize()` - Setup components
- `start()` - Start sync loop
- `stop()` - Stop sync loop
- `manual_sync()` - Force sync
- `get_status()` - Current status

---

### GUI Modules (`src/gui/`)

#### `main_window.py`
- Main application window
- Webview integration
- UI layout
- Event handling

**Key Classes:**
- `WaveAI` - Main application

**Features:**
- Embedded Perplexity webview
- Tab management UI
- Settings panel
- Status indicators

#### `perplexity_tabs.py`
- Multiple tab management
- Prompt customization per tab
- Tab state tracking

**Key Classes:**
- `PerplexityTab` - Individual tab
- `PerplexityTabManager` - Tab coordinator

**API Methods (exposed to JavaScript):**
- `create_tab()` - New tab
- `close_tab()` - Remove tab
- `switch_tab()` - Change active tab
- `set_tab_template()` - Set prompt template

#### `settings_panel.py`
- Settings UI API
- JavaScript bridge
- Configuration persistence

**Key Classes:**
- `SettingsAPI` - Settings interface

**API Methods:**
- `get_settings()` - Retrieve config
- `save_settings()` - Update config
- `start_sync()` / `stop_sync()` - Control sync
- `revert()` / `forward()` - Version control

---

### CLI Modules (`src/cli/`)

#### `commands.py`
- Command-line interface
- Click-based commands
- Colored output

**Commands:**
- `start` - Start sync engine
- `stop` - Stop sync engine
- `status` - Show status
- `sync` - Manual sync
- `revert` - Go back
- `forward` - Go forward
- `history` - View history
- `checkpoint` - Create checkpoint
- `config-show` - Display config
- `config-set` - Update config
- `init` - Setup wizard

---

### Utility Modules (`src/utils/`)

#### `logger.py`
- Structured logging
- File and console output
- Level-based filtering

**Key Classes:**
- `WaveLogger` - Custom logger

**Log Levels:**
- DEBUG - Detailed information
- INFO - General information
- WARNING - Warning messages
- ERROR - Error messages
- CRITICAL - Critical failures

#### `prompt_templates.py`
- Predefined AI prompts
- Template system
- Context injection

**Key Classes:**
- `PromptTemplates` - Template collection

**Templates:**
- `coding_assistant` - General coding
- `bug_fix` - Debugging
- `feature_dev` - New features
- `code_review` - Review code
- `refactoring` - Code improvement
- `documentation` - Write docs
- `quick_fix` - Fast fixes

#### `conflict_handler.py`
- Merge conflict detection
- Conflict parsing
- Resolution strategies

**Key Classes:**
- `ConflictHandler` - Conflict utilities

**Methods:**
- `detect_conflicts_in_file()` - Check file
- `parse_conflict()` - Parse markers
- `resolve_conflict_ours()` - Keep local
- `resolve_conflict_theirs()` - Keep remote

---

## 🔄 Data Flow

```
User Action
    ↓
┌───────────────────────────────────────────┐
│          main.py / wave-ai.py             │ Entry points
└───────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────┐
│           GUI or CLI Interface            │ User interface
└───────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────┐
│            SyncEngine                      │ Coordinator
│  ┌─────────────────────────────────────┐  │
│  │  GitSync    VersionControl          │  │
│  │  FileWatcher   ConfigManager        │  │
│  └─────────────────────────────────────┘  │
└───────────────────────────────────────────┘
    ↓                    ↓
Local Files ←──────→ GitHub ←──────→ Perplexity
```

---

## 🧩 Component Dependencies

```
main.py
  ├── src.gui.main_window
  │     ├── src.gui.perplexity_tabs
  │     ├── src.gui.settings_panel
  │     └── src.core.sync_engine
  │
  └── src.cli.commands
        └── src.core.sync_engine

sync_engine
  ├── src.core.git_sync
  ├── src.core.version_control
  ├── src.core.file_watcher
  ├── src.core.config_manager
  └── src.utils.logger

All modules use:
  ├── src.utils.logger
  └── src.core.config_manager
```

---

## 📊 Configuration Flow

```
1. User Input (GUI/CLI)
        ↓
2. ConfigManager.set()
        ↓
3. config/settings.json
        ↓
4. Components read config
        ↓
5. Apply changes
```

---

## 🔐 File Permissions

### Read-Only
- `src/**/*.py` - Source code
- `*.md` - Documentation
- `requirements.txt`

### Read-Write
- `config/settings.json` - User config
- `logs/*.log` - Application logs
- `logs/version_history.json` - Version history

### Generated
- `__pycache__/` - Python bytecode
- `*.bat` - Windows launchers

---

## 🧪 Extension Points

### Adding New Commands

1. Edit `src/cli/commands.py`
2. Add new `@cli.command()` function
3. Access `sync_engine` or `config` as needed

Example:
```python
@cli.command()
def mycommand():
    """My custom command"""
    # Your code here
    pass
```

### Adding New Prompt Templates

1. Edit `src/utils/prompt_templates.py`
2. Add new template constant
3. Update `get_template()` method
4. Update `list_templates()` method

### Custom Settings

1. Edit `ConfigManager.DEFAULT_CONFIG` in `config_manager.py`
2. Add validation in `validate()` method
3. Update settings UI if needed

---

## 📈 Performance Considerations

### Memory Usage
- **SyncEngine**: ~10-20 MB
- **FileWatcher**: ~5-10 MB  
- **GUI (webview)**: ~30-50 MB
- **Total**: ~50-100 MB typical

### CPU Usage
- **Idle**: ~2-5%
- **Syncing**: ~10-15%
- **File operations**: ~20-30%

### Disk I/O
- Logs: Append-only, minimal writes
- Config: Only on save
- Git: Standard Git I/O

---

## 🔍 Testing Structure

Currently, Wave.AI doesn't include formal tests, but you can test manually:

### Unit Testing Approach
```python
# Example test structure
import unittest
from src.core.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    def test_load_config(self):
        config = ConfigManager()
        self.assertIsNotNone(config.config)
```

### Integration Testing
```bash
# Test full workflow
python wave-ai.py init  # Setup
python wave-ai.py start # Start sync
# Make file changes
python wave-ai.py status  # Check status
python wave-ai.py revert  # Test version control
```

---

## 🚀 Future Enhancements

Possible additions:
- Unit tests (pytest)
- Integration tests
- GUI tests (Selenium)
- Performance profiling
- Code coverage reports
- CI/CD pipeline
- Docker support
- Linux/Mac compatibility
- Plugin system

---

## 📝 Code Style

- **PEP 8** compliant
- **Type hints** where appropriate
- **Docstrings** for all classes/functions
- **Comments** for complex logic
- **Logging** for debugging

---

## 🤝 Contributing

To modify Wave.AI:

1. Understand the architecture (`ARCHITECTURE.md`)
2. Review this structure document
3. Make changes in appropriate module
4. Test thoroughly
5. Update documentation
6. Commit with clear message

---

**Questions about the structure?**

- Architecture: See `ARCHITECTURE.md`
- Usage: See `README.md`
- Setup: See `SETUP_GUIDE.md`

