# ⚡ Wave.AI Quick Start

Get Wave.AI running in 5 minutes!

## Prerequisites

- ✅ Python 3.8+ installed
- ✅ Git installed  
- ✅ GitHub account
- ✅ Perplexity account

## 🚀 Installation (3 minutes)

```bash
# 1. Navigate to Wave.AI directory
cd C:\Users\YourName\Desktop\Wave.AI

# 2. Run setup
python setup.py

# 3. Configure (follow the prompts)
python wave-ai.py init
```

When prompted, enter:
- **GitHub Repo URL**: `https://github.com/yourusername/yourrepo`
- **Local Directory**: `C:/Users/YourName/Projects/MyCode`
- **Branch**: `main`
- **Sync Interval**: `30`

## 🌐 Connect Perplexity (2 minutes)

1. Go to https://www.perplexity.ai
2. Sign in → **Settings** → **Integrations**
3. Click **Connect GitHub**
4. Authorize access to your repository

## ▶️ Start Using Wave.AI

### Launch GUI
```bash
python main.py gui
```
Or double-click: **Wave.AI.bat**

### Use Perplexity

Copy this prompt into Perplexity:

```
🤖 Wave.AI Coding Mode

You are an AI coding assistant with access to my GitHub repository at https://github.com/yourusername/yourrepo

Your changes will automatically sync to my local machine via Wave.AI.

Please help me with: [describe your task]
```

### Watch It Work!

1. **Create a file locally** → Wave.AI pushes to GitHub
2. **Ask Perplexity to edit** → Changes sync back to your PC
3. **Revert anytime**: `python wave-ai.py revert`

## 📚 Learn More

- **Full Setup Guide**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Complete Documentation**: [README.md](README.md)
- **Architecture Details**: [ARCHITECTURE.md](ARCHITECTURE.md)

## 💡 Essential Commands

```bash
python wave-ai.py status    # Check sync status
python wave-ai.py sync      # Manual sync
python wave-ai.py history   # View version history
python wave-ai.py revert    # Undo last change
python wave-ai.py forward   # Redo change
```

## 🆘 Having Issues?

1. **Check logs**: `logs/wave_YYYYMMDD.log`
2. **Verify Git**: `git --version`
3. **Test manually**: `git pull` in your local directory
4. **Reconfigure**: `python wave-ai.py init`

---

**You're all set! 🎉**

Start coding with AI assistance now!

