# 🌊 Wave.AI - Free AI Coding Assistant

> A lightweight, free alternative to Cursor, Claude Code, and Windsurf - powered by Perplexity's GitHub connector.

Wave.AI is a modern AI coding assistant that combines the power of Perplexity AI with automatic GitHub synchronization, giving you a free, lightweight IDE experience without any API costs.

## ✨ Features

- 🤖 **Perplexity Integration** - Use Perplexity's GitHub connector for AI-powered code assistance
- 🔄 **Auto-Sync** - Bidirectional synchronization between local files and GitHub
- 📱 **Multi-Tab Interface** - Work on multiple features simultaneously
- ⏮️ **Version Control** - Easy revert/forward navigation through code history
- 🎨 **Modern UI** - Clean, compact, and intuitive interface
- 💰 **100% Free** - No API keys, no subscriptions, no cloud billing
- ⚡ **Lightweight** - Minimal resource usage (~50-100 MB RAM)
- 🔒 **Secure** - All data stays in your control (GitHub + Local)

## 🎯 How It Works

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Local Files    │────▶│   Wave.AI       │────▶│  GitHub Repo    │
│  (Your PC)      │◀────│   Sync Engine   │◀────│                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │
                              │
                              ▼
                        ┌─────────────────┐
                        │  Perplexity AI  │
                        │  (Web Interface)│
                        └─────────────────┘
```

1. **You** edit code locally or ask Perplexity to make changes
2. **Wave.AI** automatically syncs changes between your PC and GitHub
3. **Perplexity** (with GitHub access) can analyze and modify your repository
4. **Changes** are automatically downloaded to your local machine
5. **Version control** lets you revert or move forward through any changes

## 📋 Prerequisites

Before you start, make sure you have:

- **Windows 10/11** (with PowerShell)
- **Python 3.8+** installed
- **Git** installed and configured
- **GitHub account** (free)
- **Perplexity account** (free) with GitHub integration enabled

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
# Clone or download Wave.AI
cd C:\Users\YourName\Desktop\Wave.AI

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Link Perplexity to GitHub

1. Go to [Perplexity.ai](https://www.perplexity.ai)
2. Sign in to your account
3. Go to Settings → Integrations
4. Connect your GitHub account
5. Grant access to your repositories

### Step 3: Initial Configuration

Run the setup wizard:

```bash
python wave-ai.py init
```

You'll be asked for:
- **GitHub Repository URL** (e.g., `https://github.com/username/myproject`)
- **Local Code Directory** (e.g., `C:\Users\YourName\Projects\MyCode`)
- **Git Branch** (usually `main`)
- **Sync Interval** (seconds between syncs, default: 30)

### Step 4: Start Wave.AI

**GUI Mode (Recommended):**
```bash
python main.py gui
```

**CLI Mode:**
```bash
python wave-ai.py start
```

## 💻 Usage Guide

### GUI Mode

The GUI provides a complete interface with:

#### Main Window Components:
- **Perplexity Tabs** - Multiple browser tabs for parallel AI sessions
- **Status Indicator** - Real-time sync status
- **Settings Panel** - Configure all options
- **Version Control** - Easy revert/forward buttons
- **Sync Controls** - Manual push/pull buttons

#### Creating Multiple Tabs:
1. Click **"+ New Tab"** button
2. Each tab opens a fresh Perplexity session
3. Use different prompt templates per tab
4. Work on multiple features simultaneously

#### Using Custom Prompts:
1. Open Settings (⚙️ button)
2. Select prompt template:
   - `coding_assistant` - General coding help
   - `bug_fix` - Debug existing code
   - `feature_dev` - Build new features
   - `code_review` - Get code feedback
   - `refactoring` - Improve code structure
   - `documentation` - Create documentation
   - `quick_fix` - Fast, focused fixes

### CLI Mode

Wave.AI provides a powerful command-line interface:

```bash
# Start sync engine
python wave-ai.py start

# Check status
python wave-ai.py status

# Stop sync engine
python wave-ai.py stop

# Manual sync
python wave-ai.py sync

# Force pull from GitHub
python wave-ai.py pull

# Force push to GitHub
python wave-ai.py push

# Version control
python wave-ai.py revert          # Go back 1 version
python wave-ai.py revert --steps 5  # Go back 5 versions
python wave-ai.py forward         # Go forward 1 version
python wave-ai.py history         # Show version history
python wave-ai.py goto 42         # Go to specific checkpoint

# Create manual checkpoint
python wave-ai.py checkpoint --description "Before big refactor"

# Configuration
python wave-ai.py config-show     # Show current config
python wave-ai.py config-set github.repo_url https://github.com/user/repo
python wave-ai.py init            # Run setup wizard again
```

## 📖 Example Workflows

### Workflow 1: Adding a New Feature

1. **Start Wave.AI** in GUI mode
2. **Open Perplexity** tab
3. **Paste the custom prompt** (coding_assistant mode)
4. **Ask Perplexity:** "Add user authentication to my Flask app"
5. **Perplexity** commits changes to GitHub
6. **Wave.AI** automatically pulls changes to your local directory
7. **Test locally**, make adjustments if needed
8. **Changes auto-sync** back to GitHub

### Workflow 2: Fixing a Bug

1. **Switch** to `bug_fix` prompt template
2. **Tell Perplexity:** "My login form isn't validating emails correctly. The file is auth.py"
3. **Perplexity** analyzes the file and proposes a fix
4. **Review** changes in your local editor
5. **Test** the fix
6. If something breaks: `python wave-ai.py revert`

### Workflow 3: Code Review

1. **Create new tab** with `code_review` template
2. **Ask Perplexity:** "Review my entire codebase for security issues"
3. **Get feedback** and recommendations
4. **Implement fixes** in another tab
5. **Use version control** to checkpoint good states

### Workflow 4: Parallel Development

1. **Tab 1:** Work on frontend features
2. **Tab 2:** Fix backend bugs
3. **Tab 3:** Write documentation
4. **All changes** sync automatically
5. **Checkpoint** after completing each task

## ⚙️ Configuration

### Configuration File

Located at `config/settings.json`:

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
    "code_directory": "C:/Users/username/Projects/MyCode",
    "watch_patterns": ["*.py", "*.js", "*.html", "*.css"]
  },
  "ui": {
    "theme": "dark",
    "max_tabs": 5,
    "show_notifications": true
  },
  "perplexity": {
    "url": "https://www.perplexity.ai",
    "custom_prompt_enabled": true,
    "custom_prompt_template": "coding_assistant"
  }
}
```

### Key Settings:

| Setting | Description | Default |
|---------|-------------|---------|
| `sync_interval` | Seconds between sync checks | 30 |
| `auto_push` | Automatically push local changes | true |
| `auto_pull` | Automatically pull remote changes | true |
| `max_tabs` | Maximum Perplexity tabs | 5 |
| `theme` | UI theme (dark/light) | dark |

## 🔧 Troubleshooting

### Sync Not Working?

1. **Check Git credentials:**
   ```bash
   git config --global credential.helper manager
   ```

2. **Verify repository access:**
   ```bash
   git ls-remote https://github.com/username/repo
   ```

3. **Check logs:**
   ```
   logs/wave_YYYYMMDD.log
   ```

### Merge Conflicts?

Wave.AI detects conflicts automatically:

1. **CLI shows:** "Conflict detected"
2. **Sync pauses** automatically
3. **Resolve manually** in your editor
4. **Commit** the resolution
5. **Sync resumes** automatically

Or use version control:
```bash
python wave-ai.py revert  # Go back to before conflict
```

### Perplexity Not Accessing GitHub?

1. **Check** Perplexity Settings → Integrations
2. **Reconnect** GitHub account
3. **Verify** repository is public or access granted
4. **Refresh** Perplexity page

### Performance Issues?

1. **Increase sync interval:**
   ```bash
   python wave-ai.py config-set github.sync_interval 60
   ```

2. **Limit file patterns:**
   Edit `config/settings.json` → `watch_patterns`

3. **Reduce tabs:**
   Lower `max_tabs` in settings

## 📊 System Requirements

- **OS:** Windows 10/11 (Linux/Mac with minor modifications)
- **Python:** 3.8 or higher
- **RAM:** 512 MB minimum, 1 GB recommended
- **Disk:** 100 MB for application + your code
- **Network:** Internet connection required for sync

## 🔒 Security & Privacy

- ✅ **All code** stored on GitHub (your control)
- ✅ **No external APIs** except GitHub and Perplexity
- ✅ **No data collection** by Wave.AI
- ✅ **Open source** - audit the code yourself
- ✅ **Local processing** - sync engine runs on your PC
- ⚠️ **GitHub public repos** - Keep sensitive data in private repos
- ⚠️ **Perplexity access** - Review what Perplexity can see

## 🤝 Tips & Best Practices

### 1. Use Custom Prompts

Always paste the appropriate template prompt when starting a new Perplexity session. This helps the AI understand its role.

### 2. Create Checkpoints

Before major changes:
```bash
python wave-ai.py checkpoint --description "Before refactoring auth system"
```

### 3. Organize with Tabs

- **Tab 1:** Current feature development
- **Tab 2:** Bug fixes and maintenance  
- **Tab 3:** Code review and documentation
- **Tab 4:** Experimentation

### 4. Review Before Committing

While auto-sync is convenient, review Perplexity's changes in your local editor before they push.

### 5. Use .gitignore

Keep sensitive files out of sync:
```
# .gitignore
.env
secrets.json
*.key
config/local.json
```

### 6. Regular Maintenance

```bash
# Weekly: Clean up old checkpoints
python wave-ai.py history  # Review history
# Manually delete old checkpoints in logs/version_history.json if needed
```

## 📚 Advanced Features

### Custom Prompt Templates

Create your own templates in `src/utils/prompt_templates.py`:

```python
CUSTOM_TEMPLATE = """
Your custom prompt here...
"""
```

### Multiple Repositories

Run multiple Wave.AI instances (one per project):

```bash
# Terminal 1 - Project A
python main.py --config project_a_config.json

# Terminal 2 - Project B
python main.py --config project_b_config.json
```

### Git Hooks

Add pre-commit hooks for validation:

```bash
# .git/hooks/pre-commit
#!/bin/bash
python -m pylint src/
```

## 🐛 Known Issues

- **Windows path issues:** Use forward slashes in config: `C:/Users/...`
- **Large files:** Git may struggle with files >100MB (use Git LFS)
- **Private repos:** Ensure SSH keys or credentials are set up
- **Rapid changes:** Debounce delays (2s) prevent commit spam

## 🔄 Updating Wave.AI

```bash
# Pull latest version
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
python main.py
```

## 📝 Changelog

### Version 1.0.0 (2025-11-02)
- ✨ Initial release
- 🔄 Automatic Git synchronization
- 🤖 Perplexity integration
- 📱 Multi-tab UI
- ⏮️ Version control system
- 💻 CLI interface
- 📚 Custom prompt templates

## 🙏 Credits

- **Perplexity AI** - For providing free AI access with GitHub integration
- **GitHub** - For free repository hosting
- **Python Community** - For amazing open-source libraries

## 📄 License

This project is released under the MIT License. Feel free to use, modify, and distribute.

## 🤔 FAQ

**Q: Is this really free?**  
A: Yes! No API costs, no subscriptions. Just GitHub (free) + Perplexity (free).

**Q: How does it compare to Cursor/Windsurf?**  
A: Wave.AI is simpler and doesn't have built-in code editing, but it's 100% free and uses Perplexity's powerful AI.

**Q: Can I use private repositories?**  
A: Yes, as long as Perplexity has access to them.

**Q: What if I don't like a change?**  
A: Use `python wave-ai.py revert` to go back instantly.

**Q: Can multiple people use the same repo?**  
A: Yes, but coordinate to avoid conflicts.

**Q: Does it work with languages other than Python?**  
A: Yes! Works with any language in your repository.

## 💬 Support

- **Issues:** Check logs in `logs/` directory
- **Documentation:** See `ARCHITECTURE.md` for technical details
- **Community:** Share your experience and help others!

---

**Made with 💙 by developers, for developers**

Get started now and experience free AI-powered coding!

