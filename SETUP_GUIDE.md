# 🚀 Wave.AI Setup Guide

Complete step-by-step instructions for setting up Wave.AI on Windows.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Windows 10 or Windows 11
- [ ] Administrator access (for installing software)
- [ ] Stable internet connection
- [ ] GitHub account (free)
- [ ] Perplexity account (free)

---

## Step 1: Install Python (15 minutes)

### 1.1 Download Python

1. Go to https://www.python.org/downloads/
2. Click "Download Python 3.11.x" (or latest version)
3. Run the installer

### 1.2 Install Python

**IMPORTANT:** Check these boxes during installation:
- ✅ **Add Python to PATH** (critical!)
- ✅ Install pip
- ✅ Install for all users (if you have admin rights)

### 1.3 Verify Installation

Open PowerShell or Command Prompt:

```bash
python --version
```

Should show: `Python 3.11.x` or higher

```bash
pip --version
```

Should show: `pip 23.x.x` or similar

✅ **Python installed successfully!**

---

## Step 2: Install Git (10 minutes)

### 2.1 Download Git

1. Go to https://git-scm.com/downloads
2. Download "Git for Windows"
3. Run the installer

### 2.2 Install Git

Use default settings, but pay attention to:
- ✅ Use Git from Windows Command Prompt
- ✅ Use OpenSSL library
- ✅ Checkout Windows-style, commit Unix-style line endings
- ✅ Use Windows default console window

### 2.3 Configure Git

Open PowerShell:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 2.4 Set up Git Credential Manager

```bash
git config --global credential.helper manager
```

This will store your GitHub credentials securely.

### 2.5 Verify Installation

```bash
git --version
```

Should show: `git version 2.x.x`

✅ **Git installed successfully!**

---

## Step 3: Set Up GitHub Repository (5 minutes)

### 3.1 Create a Repository

**Option A: Create New Repository**

1. Go to https://github.com
2. Click the "+" icon → "New repository"
3. Repository name: `my-wave-ai-project`
4. Description: "My coding project with Wave.AI"
5. **Choose:**
   - ✅ Public (required for free Perplexity access)
   - ✅ Add a README
6. Click "Create repository"

**Option B: Use Existing Repository**

Skip to Step 3.2 and use your existing repo URL.

### 3.2 Get Repository URL

Copy your repository URL:
```
https://github.com/yourusername/my-wave-ai-project
```

### 3.3 Clone Repository Locally (Optional)

If you want to start with existing code:

```bash
cd C:\Users\YourName\Projects
git clone https://github.com/yourusername/my-wave-ai-project
```

Or create a new directory:

```bash
mkdir C:\Users\YourName\Projects\MyCode
cd C:\Users\YourName\Projects\MyCode
git init
git remote add origin https://github.com/yourusername/my-wave-ai-project
```

✅ **GitHub repository ready!**

---

## Step 4: Connect Perplexity to GitHub (5 minutes)

### 4.1 Create Perplexity Account

1. Go to https://www.perplexity.ai
2. Click "Sign Up" (or "Log In" if you have an account)
3. Create account with email/Google/GitHub

### 4.2 Enable GitHub Integration

1. Click your profile picture (top right)
2. Go to **Settings**
3. Click **Integrations** or **Connected Accounts**
4. Find **GitHub** and click **Connect**
5. Authorize Perplexity to access your GitHub
6. **Grant access** to your repositories:
   - Select "All repositories" or
   - Select specific repository

### 4.3 Verify Connection

1. In Perplexity, type: "What files are in my repository [repo-name]?"
2. Perplexity should list your files

✅ **Perplexity connected to GitHub!**

---

## Step 5: Install Wave.AI (10 minutes)

### 5.1 Download Wave.AI

**Option A: Download as ZIP**
1. Go to Wave.AI repository or location
2. Download ZIP file
3. Extract to: `C:\Users\YourName\Desktop\Wave.AI`

**Option B: Clone with Git**
```bash
cd C:\Users\YourName\Desktop
git clone https://github.com/yourusername/wave-ai
cd wave-ai
```

### 5.2 Run Setup Script

Open PowerShell in Wave.AI directory:

```bash
cd C:\Users\YourName\Desktop\Wave.AI
python setup.py
```

The script will:
- ✅ Check Python version
- ✅ Check Git installation
- ✅ Install dependencies
- ✅ Create necessary directories
- ✅ Configure Git credentials
- ✅ Create launcher scripts

**This may take 5-10 minutes** to download and install packages.

### 5.3 Initial Configuration

The setup script will ask:

```
Run configuration wizard? (y/n):
```

Type `y` and press Enter.

You'll be prompted for:

1. **GitHub Repository URL:**
   ```
   https://github.com/yourusername/my-wave-ai-project
   ```

2. **Local Code Directory:**
   ```
   C:/Users/YourName/Projects/MyCode
   ```
   (Use forward slashes!)

3. **Git Branch:**
   ```
   main
   ```
   (or `master` if your repo uses that)

4. **Sync Interval (seconds):**
   ```
   30
   ```
   (how often to check for changes)

✅ **Wave.AI installed and configured!**

---

## Step 6: First Launch (5 minutes)

### 6.1 Start Wave.AI GUI

**Option A: Double-click launcher**
```
Wave.AI.bat
```

**Option B: Command line**
```bash
python main.py gui
```

### 6.2 What You'll See

The Wave.AI window will open with:
- 🌊 **Wave.AI** logo in toolbar
- **Perplexity tab** loading
- **Status indicator** (orange = idle, green = syncing)
- **Settings button** (⚙️)
- **New Tab button** (+)

### 6.3 First Sync Test

1. Click **Settings** (⚙️)
2. Verify your configuration is correct
3. Close settings
4. The app will automatically:
   - Initialize Git sync
   - Connect to your repository
   - Start monitoring for changes

Check the status indicator - it should turn green!

✅ **Wave.AI is running!**

---

## Step 7: Test the Workflow (10 minutes)

### 7.1 Create a Test File Locally

In your local directory (`C:\Users\YourName\Projects\MyCode`):

1. Create a new file: `test.py`
2. Add some code:
   ```python
   def hello():
       print("Hello from Wave.AI!")
   ```
3. Save the file

### 7.2 Watch Auto-Sync

Wave.AI will automatically:
- Detect the new file (within ~2 seconds)
- Commit it with message like: `[Wave.AI Auto] 2025-11-02 14:30:00: test.py`
- Push to GitHub

Check GitHub - your file should appear!

### 7.3 Test Perplexity Integration

1. In Wave.AI, the Perplexity tab should be loaded
2. Copy this prompt:

```
🤖 Wave.AI Coding Mode

You are an AI coding assistant integrated with Wave.AI. You have direct access to my GitHub repository at https://github.com/yourusername/my-wave-ai-project and can make changes to the codebase.

Your changes will be automatically committed and synced to my local machine.

Please add a new function to test.py that calculates the factorial of a number.
```

3. Paste into Perplexity and send
4. Perplexity will:
   - Access your GitHub repository
   - Modify `test.py`
   - Commit the changes

### 7.4 Watch Changes Sync Back

Wave.AI will automatically:
- Detect GitHub has new commits (within 30 seconds)
- Pull the changes
- Update your local `test.py` file
- Show notification

Open `test.py` locally - you'll see Perplexity's changes!

### 7.5 Test Version Control

```bash
# In PowerShell, in Wave.AI directory
python wave-ai.py history
```

You'll see your commit history.

To revert:
```bash
python wave-ai.py revert
```

Your file goes back to the previous version!

To move forward again:
```bash
python wave-ai.py forward
```

✅ **Everything is working!**

---

## 🎯 Quick Reference

### Starting Wave.AI

**GUI Mode:**
```bash
python main.py gui
# or double-click Wave.AI.bat
```

**CLI Mode:**
```bash
python wave-ai.py start
```

### Common Commands

```bash
# Check status
python wave-ai.py status

# Manual sync
python wave-ai.py sync

# Version control
python wave-ai.py history
python wave-ai.py revert
python wave-ai.py forward

# Configuration
python wave-ai.py config-show
python wave-ai.py init
```

### File Locations

- **Configuration:** `config/settings.json`
- **Logs:** `logs/wave_YYYYMMDD.log`
- **Version History:** `logs/version_history.json`

---

## 🔧 Troubleshooting Common Issues

### Issue: "Python not recognized"

**Fix:**
1. Reinstall Python
2. **Check** "Add Python to PATH"
3. Restart PowerShell

### Issue: "Git not recognized"

**Fix:**
1. Reinstall Git
2. Choose "Use Git from Windows Command Prompt"
3. Restart PowerShell

### Issue: "Repository not found"

**Fix:**
- Check repository URL in settings
- Ensure repository is public
- Check Git credentials: `git credential-manager`

### Issue: "Permission denied (publickey)"

**Fix:**
```bash
# Set up SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"
# Add to GitHub: Settings → SSH Keys
```

Or use HTTPS instead of SSH URLs.

### Issue: "Perplexity can't access my repo"

**Fix:**
1. Go to Perplexity Settings → Integrations
2. Disconnect and reconnect GitHub
3. Ensure repository access is granted
4. Repository must be public or access granted

### Issue: "Sync not working"

**Fix:**
1. Check logs: `logs/wave_YYYYMMDD.log`
2. Verify credentials: Try `git pull` manually in local directory
3. Check sync settings in `config/settings.json`
4. Restart Wave.AI

### Issue: "Import errors when starting"

**Fix:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

---

## 📚 Next Steps

Now that Wave.AI is set up:

1. **Read README.md** - Learn all features
2. **Try different prompt templates** - Optimize for different tasks
3. **Use multiple tabs** - Work on parallel features
4. **Create checkpoints** - Before major changes
5. **Experiment!** - It's all version controlled, you can always revert

---

## 🎓 Learning Resources

### Understanding Git
- https://git-scm.com/doc
- https://learngitbranching.js.org/

### Perplexity GitHub Integration
- https://www.perplexity.ai/hub/integrations

### Python Basics
- https://www.python.org/about/gettingstarted/

---

## 🆘 Getting Help

If you're stuck:

1. **Check logs:** `logs/` directory
2. **Review settings:** `config/settings.json`
3. **Verify manually:**
   ```bash
   cd YourLocalDirectory
   git status
   git pull
   ```
4. **Reset if needed:**
   ```bash
   python wave-ai.py init
   ```

---

**Congratulations! 🎉**

You're now ready to use Wave.AI for AI-powered coding!

Start by asking Perplexity to help with your project, and watch the magic happen.

Happy coding! 🌊

