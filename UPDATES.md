# Wave.AI Updates & Fixes

## Latest Updates (2025-11-02)

### 🔧 Bug Fixes

#### 1. **Fixed Dependency Installation**
- **Issue**: `pywin32==306` not available for Python 3.13
- **Fix**: Updated `requirements.txt` to use `pywin32>=307` with platform check
- **Impact**: Now compatible with Python 3.8 through 3.13

#### 2. **Fixed ConfigManager Initialization**
- **Issue**: `AttributeError` when creating config file
- **Fix**: Restructured initialization order to set `self.config` before calling `save()`
- **Impact**: Setup wizard now works correctly

### ✨ New Features

#### 1. **Perplexity Browser Integration**
- **Problem**: Webview had CORS issues with Perplexity
- **Solution**: Added "Open Perplexity in Browser" button
- **How it works**: Opens Perplexity in your default browser instead of embedded iframe
- **Benefit**: Avoids security restrictions, better performance

#### 2. **GUI Sync Controls**
- **New Buttons**: 
  - 🚀 **Open Perplexity** - Opens Perplexity.ai in browser
  - ▶️ **Start Sync** - Starts automatic synchronization
  - ⏸️ **Stop Sync** - Stops synchronization
- **Real-time Status**: Shows current sync status on dashboard
- **Updates**: Status refreshes every 5 seconds automatically

#### 3. **Full Repository Clone**
- **Old Behavior**: Only cloned single branch
- **New Behavior**: Clones ALL branches from repository
- **Benefits**:
  - Access all branches locally
  - Can switch between branches easily
  - Full repository history available
- **New Command**: `python wave-ai.py branches` - List all local and remote branches

### 📊 Enhanced Dashboard

The GUI now shows:
- **Sync Status**: Running/Stopped with color indicators
- **Repository Info**: Current repo URL
- **Local Directory**: Path to local code
- **Quick Actions**: Start/Stop sync with one click
- **Auto-refresh**: Status updates every 5 seconds

---

## Usage Examples

### Starting Wave.AI

```bash
# Run setup (first time only)
python setup.py

# Configure (first time only)
python wave-ai.py init

# Start GUI
python main.py gui
```

### Using the GUI

1. **Launch Wave.AI**:
   ```bash
   python main.py gui
   ```

2. **Click "Open Perplexity"**: Opens Perplexity in your browser

3. **Click "Start Sync"**: Begins automatic synchronization

4. **Work with Perplexity**:
   - Copy custom prompt from templates
   - Paste into Perplexity
   - Ask Perplexity to modify your code
   - Changes sync automatically!

5. **Click "Stop Sync"** when you want to pause

### CLI Commands

```bash
# List all branches
python wave-ai.py branches

# Start sync
python wave-ai.py start

# Check status
python wave-ai.py status

# View history
python wave-ai.py history

# Revert changes
python wave-ai.py revert

# Stop sync
python wave-ai.py stop
```

---

## Technical Changes

### Files Modified

1. **requirements.txt**
   - Updated dependency versions
   - Added platform-specific checks
   - Compatible with Python 3.8-3.13

2. **src/core/config_manager.py**
   - Fixed initialization order
   - Added safety check before save

3. **src/core/git_sync.py**
   - Enhanced clone to fetch all branches
   - Added `get_all_branches()` method
   - Auto-creates local tracking branches

4. **src/gui/main_window.py**
   - Removed embedded iframe
   - Added dashboard with controls
   - Added JavaScript API calls
   - Real-time status updates

5. **src/gui/settings_panel.py**
   - Added `openPerplexityBrowser()` method
   - Enhanced API for JavaScript

6. **src/cli/commands.py**
   - Added `branches` command
   - List local and remote branches

---

## Migration Guide

### If You Already Have Wave.AI Installed

1. **Pull latest changes**:
   ```bash
   cd C:\Users\YourName\Desktop\Wave.AI
   git pull  # if cloned from git
   ```

2. **Update dependencies**:
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt --upgrade
   ```

3. **No config changes needed** - existing settings remain compatible

### For New Installations

Just follow the QUICKSTART.md or SETUP_GUIDE.md as normal.

---

## Known Issues & Solutions

### Issue: Perplexity won't load
**Status**: ✅ Fixed
**Solution**: Now opens in browser instead of embedded view

### Issue: Can't access other branches
**Status**: ✅ Fixed
**Solution**: All branches are now cloned automatically

### Issue: Can't stop sync from GUI
**Status**: ✅ Fixed
**Solution**: Added Stop Sync button

---

## Upcoming Features

Planned for future versions:
- [ ] Multiple repository support
- [ ] Branch switching in GUI
- [ ] Conflict resolution UI
- [ ] Diff viewer
- [ ] Commit history viewer
- [ ] Custom keyboard shortcuts
- [ ] Notification system
- [ ] Auto-update checker

---

## Changelog

### v1.0.1 (2025-11-02)
- Fixed Python 3.13 compatibility
- Fixed config initialization bug
- Added browser-based Perplexity integration
- Added GUI sync controls (Start/Stop)
- Enhanced Git clone to fetch all branches
- Added `branches` CLI command
- Improved dashboard UI
- Real-time status updates

### v1.0.0 (2025-11-02)
- Initial release
- Full sync engine
- Version control system
- GUI and CLI interfaces
- Prompt templates

---

## Getting Help

- **Quick Start**: `QUICKSTART.md`
- **Full Setup**: `SETUP_GUIDE.md`
- **Troubleshooting**: `TROUBLESHOOTING.md`
- **Architecture**: `ARCHITECTURE.md`
- **CLI Help**: `python wave-ai.py --help`

---

**Last Updated**: November 2, 2025

