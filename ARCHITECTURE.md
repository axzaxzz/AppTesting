# Wave.AI Architecture Overview

## 🎯 Project Vision
A free, lightweight AI coding IDE inspired by Cursor, Claude Code, Windsurf, and Warp.dev - powered by Perplexity's GitHub connector.

## 🏗️ System Architecture

### Data Flow Diagram
```
Local PC Directory ←→ Git Sync Engine ←→ GitHub Repository ←→ Perplexity AI (Web Interface)
                          ↓
                    Version Control
                    (Revert/Forward)
                          ↓
                      CLI/GUI Interface
```

### Component Breakdown

#### 1. **Local Directory**
- Your actual code files on Windows PC
- Monitored by file watcher for changes
- Automatically synced to GitHub

#### 2. **Git Sync Engine**
- **Auto-Pull**: Checks GitHub every N seconds for changes
- **Auto-Push**: Commits and pushes local changes automatically
- **Conflict Handling**: Detects merge conflicts and logs them
- **Change Detection**: Uses file system monitoring

#### 3. **GitHub Repository**
- Central source of truth
- Public repo linked to Perplexity
- Stores all code versions and history

#### 4. **Perplexity Web Interface**
- Embedded webview in the app
- Login with Perplexity account (GitHub connected)
- Multi-tab support for parallel AI sessions
- Custom prompts to guide AI behavior

#### 5. **Version Control System**
- Local commit history with timestamps
- Revert: Go back to previous versions
- Forward: Restore newer versions
- Uses Git tags for checkpoint management

#### 6. **GUI Application**
- Modern, clean, compact UI
- Settings panel for configuration
- Multiple Perplexity tabs
- Sync status indicators
- Dark/Light mode support

---

## 🔄 Detailed Data Flow

### Scenario 1: Perplexity Makes Changes
1. You write a prompt in Perplexity webview (e.g., "Add authentication to my app")
2. Perplexity (with GitHub access) commits changes to your GitHub repo
3. Local sync engine detects new commits on GitHub
4. Auto-pull downloads changes to local directory
5. File watcher detects new local changes
6. GUI shows notification: "Synced from GitHub"

### Scenario 2: You Edit Files Locally
1. You edit code in your local directory (any editor)
2. File watcher detects changes
3. Sync engine commits changes with timestamp
4. Auto-push uploads to GitHub
5. Changes now visible to Perplexity for analysis

### Scenario 3: Conflict Resolution
1. Both you and Perplexity edit the same file
2. Git detects merge conflict
3. Sync engine pauses and logs the conflict
4. GUI shows alert with conflict details
5. User resolves manually or chooses version
6. Sync resumes after resolution

---

## 🛠️ Technology Stack

### Core Technologies
- **Python 3.8+**: Main programming language
- **Git**: Version control system
- **PyQt6/Electron**: GUI framework
- **watchdog**: File system monitoring
- **GitPython**: Git operations in Python
- **requests**: HTTP operations (if needed)

### Windows-Specific
- **PowerShell**: For some automation tasks
- **pywebview**: Lightweight webview for embedding Perplexity

---

## 📁 Project Structure

```
Wave.AI/
├── src/
│   ├── core/
│   │   ├── git_sync.py          # Git operations (pull/push/commit)
│   │   ├── version_control.py   # Revert/forward functionality
│   │   ├── file_watcher.py      # Monitor local directory changes
│   │   ├── config_manager.py    # Settings management
│   │   └── sync_engine.py       # Main sync loop coordinator
│   ├── gui/
│   │   ├── main_window.py       # Main application window
│   │   ├── settings_panel.py    # Settings UI
│   │   ├── perplexity_tabs.py   # Multi-tab webview manager
│   │   └── styles.py            # UI styling (clean/modern)
│   ├── cli/
│   │   └── commands.py          # CLI interface
│   └── utils/
│       ├── logger.py            # Logging system
│       ├── prompt_templates.py  # Custom Perplexity prompts
│       └── conflict_handler.py  # Git conflict resolution
├── scripts/
│   ├── setup.py                 # Initial setup script
│   └── install_deps.py          # Dependency installer
├── config/
│   └── settings.json            # User configuration
├── logs/
│   └── sync.log                 # Sync history
├── requirements.txt             # Python dependencies
├── README.md                    # User guide
├── ARCHITECTURE.md              # This file
└── main.py                      # Entry point
```

---

## ⚙️ Configuration System

### settings.json Structure
```json
{
  "github": {
    "repo_url": "https://github.com/username/repo",
    "branch": "main",
    "auto_push": true,
    "auto_pull": true,
    "sync_interval": 30
  },
  "local": {
    "code_directory": "C:/Users/janny/Projects/MyCode",
    "watch_patterns": ["*.py", "*.js", "*.html", "*.css"]
  },
  "perplexity": {
    "url": "https://www.perplexity.ai",
    "custom_prompt_enabled": true,
    "custom_prompt_template": "prompt_coding_assistant"
  },
  "ui": {
    "theme": "dark",
    "max_tabs": 5,
    "show_notifications": true
  },
  "sync": {
    "commit_prefix": "[Wave.AI Auto]",
    "conflict_strategy": "manual"
  }
}
```

---

## 🔐 Security & Safety

### Git Safety Measures
1. **Never force push** - Always safe merges
2. **Backup before revert** - Create safety tags
3. **Conflict detection** - Pause on conflicts
4. **Commit validation** - Verify before push
5. **Credential security** - Use Git credential manager

### File Safety
1. **Ignore sensitive files** - Respect .gitignore
2. **Pre-commit hooks** - Validate code before commit
3. **Rollback capability** - Any change can be undone

---

## 🚀 Key Features

### 1. Automatic Synchronization
- Continuous background sync
- Smart change detection
- Minimal performance impact

### 2. Version Control
- Complete Git history
- Easy revert/forward navigation
- Checkpoint system with tags

### 3. Multi-Tab Perplexity
- Work on multiple features simultaneously
- Each tab with custom context
- Synchronized state across tabs

### 4. Custom Prompts
- Pre-configured templates
- Context-aware prompting
- Repository structure awareness

### 5. Clean Modern UI
- Minimalist design
- Responsive layout
- Status indicators
- Dark/Light themes

---

## 📊 Performance Considerations

### Optimization Strategies
1. **Debounced file watching** - Batch rapid changes
2. **Smart diff detection** - Only sync changed files
3. **Async operations** - Non-blocking sync
4. **Efficient Git operations** - Shallow clones, sparse checkouts
5. **Memory management** - Cleanup old logs

### Resource Usage (Estimated)
- **CPU**: ~2-5% idle, ~10-15% during sync
- **RAM**: ~50-100 MB
- **Disk**: Minimal (just Git objects)
- **Network**: Only when syncing

---

## 🔄 Sync Loop Algorithm

```python
while sync_active:
    # Check for remote changes
    remote_changes = check_github_updates()
    if remote_changes:
        pull_and_merge()
        notify_user("Synced from GitHub")
    
    # Check for local changes
    local_changes = file_watcher.get_changes()
    if local_changes:
        commit_and_push(local_changes)
        notify_user("Pushed to GitHub")
    
    # Handle conflicts
    if conflict_detected():
        pause_sync()
        alert_user_for_resolution()
    
    # Wait before next cycle
    sleep(sync_interval)
```

---

## 🎨 UI/UX Design Principles

### Visual Design
- **Clean**: Minimal clutter, focus on code
- **Modern**: Contemporary design patterns
- **Compact**: Efficient use of space
- **Intuitive**: Self-explanatory interface

### User Experience
- **Fast**: Instant feedback on actions
- **Reliable**: Clear status indicators
- **Forgiving**: Easy undo/redo
- **Informative**: Helpful tooltips and logs

---

## 🔧 Extensibility

### Future Enhancement Options
1. Support for multiple repositories
2. Custom file filters per project
3. Integration with other AI providers
4. Plugin system for custom workflows
5. Team collaboration features
6. Advanced conflict resolution UI
7. Code review mode
8. Performance analytics dashboard

---

## 📝 Development Phases

### Phase 1: Core Functionality ✅
- Git sync engine
- Version control system
- CLI interface
- Basic configuration

### Phase 2: GUI Development
- Main window with webview
- Settings panel
- Multi-tab system
- Status indicators

### Phase 3: Polish & Features
- Custom prompts
- Conflict handling UI
- File watching optimization
- Comprehensive testing

### Phase 4: Documentation & Distribution
- Setup guide
- Usage examples
- Troubleshooting guide
- Packaging for Windows

---

## 🎯 Success Criteria

✓ Automatic bidirectional sync (GitHub ↔ Local)
✓ Reliable version control with revert/forward
✓ Working Perplexity integration via webview
✓ Multi-tab support for parallel AI sessions
✓ Clean, modern, responsive UI
✓ Zero cost (no paid APIs or services)
✓ Lightweight (< 100 MB RAM usage)
✓ Easy setup (< 10 minutes to get running)

---

**Last Updated**: November 2, 2025
**Version**: 1.0.0

