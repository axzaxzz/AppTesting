# 🔧 Wave.AI Troubleshooting Guide

Solutions to common problems and issues.

---

## 🚨 Installation Issues

### Python Not Found

**Symptom:** `'python' is not recognized as an internal or external command`

**Solution:**
1. Reinstall Python from https://python.org
2. ✅ **Check "Add Python to PATH"** during installation
3. Restart Command Prompt/PowerShell
4. Verify: `python --version`

**Alternative:**
Try using `py` instead of `python`:
```bash
py --version
py setup.py
```

### Git Not Found

**Symptom:** `'git' is not recognized as an internal or external command`

**Solution:**
1. Install Git from https://git-scm.com
2. Choose "Use Git from Windows Command Prompt"
3. Restart Command Prompt/PowerShell
4. Verify: `git --version`

### Pip Install Fails

**Symptom:** `ERROR: Could not install packages...`

**Solution 1 - Update pip:**
```bash
python -m pip install --upgrade pip
python setup.py
```

**Solution 2 - Use virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Solution 3 - Admin rights:**
Run PowerShell as Administrator

---

## 🔄 Sync Issues

### Sync Not Working

**Symptom:** Changes not syncing between local and GitHub

**Check 1 - Status:**
```bash
python wave-ai.py status
```
Look for errors in the output.

**Check 2 - Logs:**
Open `logs/wave_YYYYMMDD.log` and look for errors.

**Check 3 - Git credentials:**
```bash
cd YourLocalDirectory
git pull
```
If it asks for credentials, configure:
```bash
git config --global credential.helper manager
```

**Check 4 - Repository access:**
- Ensure repository URL is correct
- For private repos, ensure you have access
- Try cloning manually: `git clone <repo-url>`

### Authentication Failed

**Symptom:** `Authentication failed` or `Permission denied`

**Solution 1 - HTTPS (Recommended for Windows):**
```bash
# Use HTTPS URL
https://github.com/username/repo.git

# Configure credential manager
git config --global credential.helper manager

# Next git operation will prompt for credentials
```

**Solution 2 - Personal Access Token:**
1. GitHub → Settings → Developer Settings → Personal Access Tokens
2. Generate new token with `repo` scope
3. Use token as password when prompted

**Solution 3 - SSH:**
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add to SSH agent
ssh-add ~/.ssh/id_ed25519

# Add public key to GitHub
# Settings → SSH Keys → Add New
```

### Push Rejected

**Symptom:** `error: failed to push some refs`

**Solution:**
```bash
# Pull first, then push
python wave-ai.py pull
python wave-ai.py push

# Or force sync
python wave-ai.py sync
```

---

## 🔗 Perplexity Issues

### Perplexity Can't Access Repository

**Symptom:** Perplexity says "I don't have access to that repository"

**Solution:**
1. Go to https://www.perplexity.ai/settings
2. Integrations → GitHub → **Reconnect**
3. Authorize all repositories or select specific repo
4. **Verify:** Ask Perplexity to list files in your repo

### Perplexity Changes Not Syncing

**Symptom:** Perplexity commits to GitHub but changes don't appear locally

**Check 1 - Auto-pull enabled:**
```bash
python wave-ai.py config-show
```
Ensure `auto_pull: true`

**Check 2 - Sync engine running:**
```bash
python wave-ai.py status
```
Should show "Status: Running"

**Check 3 - Manual pull:**
```bash
python wave-ai.py pull
```

**Check 4 - Sync interval:**
Changes sync every 30 seconds by default. Wait a bit or:
```bash
python wave-ai.py config-set github.sync_interval 10
```

### Repository Not Public

**Symptom:** Perplexity requires public repository

**Solution:**
Make repository public or ensure Perplexity has access:
1. GitHub → Your Repo → Settings → Danger Zone
2. "Change visibility" → Public

Or grant Perplexity access to private repos in GitHub settings.

---

## 🐛 Runtime Errors

### Import Errors

**Symptom:** `ModuleNotFoundError: No module named 'watchdog'`

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### File Path Errors

**Symptom:** `FileNotFoundError` or `Path does not exist`

**Solution:**
Use forward slashes in config:
```json
{
  "local": {
    "code_directory": "C:/Users/YourName/Projects/MyCode"
  }
}
```

NOT backward slashes: `C:\Users\...`

### Permission Errors

**Symptom:** `PermissionError: [WinError 5] Access is denied`

**Solution:**
1. Close any programs using the files
2. Run as Administrator
3. Check antivirus isn't blocking
4. Verify folder permissions

---

## ⚠️ Merge Conflicts

### Conflict Detected

**Symptom:** `Conflict detected` in logs

**Solution 1 - Revert:**
```bash
# Go back to before conflict
python wave-ai.py revert
```

**Solution 2 - Use local version:**
1. Edit conflicted files manually
2. Remove conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
3. Keep the version you want
4. Save and commit

**Solution 3 - Use remote version:**
```bash
cd YourLocalDirectory
git checkout --theirs .
git add .
git commit -m "Resolved conflicts"
```

**Solution 4 - Manual resolution:**
```bash
# Open conflicted file in editor
# Look for:
<<<<<<< HEAD
Your local changes
=======
Remote changes
>>>>>>> branch

# Edit to keep what you want
# Remove markers
# Save
git add .
git commit -m "Resolved conflicts"
```

---

## 🖥️ GUI Issues

### GUI Won't Start

**Symptom:** `python main.py gui` doesn't open window

**Solution 1 - Check dependencies:**
```bash
pip install pywebview --upgrade
```

**Solution 2 - Try CLI instead:**
```bash
python wave-ai.py start
```

**Solution 3 - Check logs:**
```bash
logs/wave_YYYYMMDD.log
```

### Webview Blank

**Symptom:** Window opens but Perplexity doesn't load

**Solution:**
1. Check internet connection
2. Try opening https://www.perplexity.ai in browser
3. Check firewall/antivirus settings
4. Update config:
```bash
python wave-ai.py config-set perplexity.url https://www.perplexity.ai
```

---

## 📁 File Watching Issues

### Changes Not Detected

**Symptom:** Local file changes not pushing to GitHub

**Check 1 - File patterns:**
Edit `config/settings.json`:
```json
{
  "local": {
    "watch_patterns": ["*"]
  }
}
```

**Check 2 - Restart sync:**
```bash
python wave-ai.py stop
python wave-ai.py start
```

**Check 3 - Manual push:**
```bash
python wave-ai.py push
```

### Too Many Commits

**Symptom:** Every small change creates a commit

**Solution - Increase debounce:**
Edit `src/core/file_watcher.py`:
```python
# Change debounce_seconds to higher value (default: 2.0)
debounce_seconds = 5.0  # Wait 5 seconds
```

---

## 🔐 Configuration Issues

### Settings Not Saving

**Symptom:** Changes to settings don't persist

**Solution:**
```bash
# Verify config file exists
dir config\settings.json

# Recreate if needed
python wave-ai.py init
```

### Invalid Configuration

**Symptom:** `Configuration errors`

**Solution:**
```bash
# Validate config
python wave-ai.py init

# Or manually edit
notepad config\settings.json

# Use forward slashes
# Ensure valid JSON format
```

---

## 🗂️ Version Control Issues

### Can't Revert

**Symptom:** `Cannot revert, no history`

**Solution:**
Version history starts after first checkpoint:
```bash
python wave-ai.py checkpoint --description "Initial state"
# Make some changes
python wave-ai.py checkpoint --description "After changes"
# Now you can revert
python wave-ai.py revert
```

### History Missing

**Symptom:** `No version history available`

**Check:**
```bash
dir logs\version_history.json
```

If missing, it will be created on next checkpoint.

---

## 💾 Storage Issues

### Repository Too Large

**Symptom:** `file is too large` errors

**Solution - Git LFS:**
```bash
git lfs install
git lfs track "*.psd"
git lfs track "*.zip"
git add .gitattributes
git commit -m "Add Git LFS"
```

### Disk Space

**Symptom:** Sync fails due to disk space

**Solution:**
1. Clean up logs: `del logs\*.log`
2. Clean Git: `cd YourRepo && git gc`
3. Remove old checkpoints: Edit `logs/version_history.json`

---

## 🌐 Network Issues

### Connection Timeout

**Symptom:** `Connection timeout` or `Unable to connect`

**Solution:**
1. Check internet connection
2. Try accessing GitHub.com in browser
3. Check proxy settings:
```bash
git config --global http.proxy http://proxy.server:port
```
4. Increase timeout:
```bash
git config --global http.postBuffer 524288000
```

### Rate Limiting

**Symptom:** `API rate limit exceeded`

**Solution:**
Wait a few minutes, or authenticate with token.

---

## 🖱️ Common User Errors

### Wrong Directory

**Problem:** Editing files outside configured directory

**Solution:**
Ensure you're editing files in the directory configured in settings:
```bash
python wave-ai.py config-show
```

### Wrong Branch

**Problem:** Changes on different branch

**Solution:**
```bash
cd YourLocalDirectory
git branch  # Check current branch
git checkout main  # Switch to main
```

### Forgot to Start Sync

**Problem:** Made changes but sync not running

**Solution:**
```bash
python wave-ai.py start
```

---

## 🆘 Emergency Recovery

### Everything Broken

**Nuclear option - Start fresh:**

```bash
# Backup your code!
# Then:

# 1. Stop sync
python wave-ai.py stop

# 2. Backup config
copy config\settings.json config\settings.backup.json

# 3. Clean slate
rd /s config\settings.json
rd /s logs

# 4. Reconfigure
python wave-ai.py init

# 5. Restore code from GitHub
cd YourLocalDirectory
git fetch origin
git reset --hard origin/main
```

---

## 📞 Getting More Help

### Diagnostic Information

When asking for help, provide:

```bash
# System info
python --version
git --version

# Wave.AI status
python wave-ai.py status

# Recent logs (last 50 lines)
# Windows PowerShell:
Get-Content logs\wave_*.log -Tail 50
```

### Log Files

Check these files:
- `logs/wave_YYYYMMDD.log` - Application logs
- `logs/version_history.json` - Version control history
- `config/settings.json` - Your configuration

---

## ✅ Preventive Measures

### Best Practices

1. **Regular checkpoints:**
```bash
python wave-ai.py checkpoint --description "Before major changes"
```

2. **Monitor status:**
```bash
python wave-ai.py status
```

3. **Review logs:**
```bash
notepad logs\wave_*.log
```

4. **Keep backups:**
- Your code is on GitHub (backup!)
- Export config: `copy config\settings.json backup\`

5. **Test before big changes:**
```bash
# Create test branch
cd YourRepo
git checkout -b test
# Make changes
# If good, merge. If bad, revert:
git checkout main
```

---

**Still having issues?**

1. Read the full documentation: `README.md`
2. Check architecture: `ARCHITECTURE.md`
3. Review logs in `logs/` directory
4. Try the quickstart: `QUICKSTART.md`

Most issues are configuration-related. Double-check your settings!

