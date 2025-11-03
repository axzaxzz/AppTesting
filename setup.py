"""
Wave.AI Setup Script
Installs dependencies and configures the environment
"""

import subprocess
import sys
import os
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def check_python_version():
    """Check if Python version is compatible"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ERROR: Python 3.8 or higher is required")
        print("Please install Python 3.8+ from https://www.python.org/downloads/")
        return False
    
    print("✓ Python version is compatible")
    return True


def check_git_installed():
    """Check if Git is installed"""
    print_header("Checking Git Installation")
    
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        print(f"Git version: {result.stdout.strip()}")
        print("✓ Git is installed")
        return True
    except FileNotFoundError:
        print("❌ ERROR: Git is not installed")
        print("Please install Git from https://git-scm.com/downloads")
        return False


def install_dependencies():
    """Install Python dependencies"""
    print_header("Installing Dependencies")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ ERROR: requirements.txt not found")
        return False
    
    print("Installing Python packages...")
    print("This may take a few minutes...\n")
    
    try:
        subprocess.check_call([
            sys.executable,
            '-m',
            'pip',
            'install',
            '-r',
            str(requirements_file),
            '--upgrade'
        ])
        print("\n✓ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERROR: Failed to install dependencies: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    print_header("Creating Directories")
    
    directories = [
        'config',
        'logs',
        'src/core',
        'src/gui',
        'src/cli',
        'src/utils'
    ]
    
    for directory in directories:
        dir_path = Path(__file__).parent / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {directory}")
    
    return True


def configure_git():
    """Configure Git settings"""
    print_header("Configuring Git")
    
    try:
        # Check if Git user is configured
        result = subprocess.run(
            ['git', 'config', '--global', 'user.name'],
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            print("Git user not configured. Please enter your details:")
            name = input("Your name: ")
            email = input("Your email: ")
            
            subprocess.run(['git', 'config', '--global', 'user.name', name])
            subprocess.run(['git', 'config', '--global', 'user.email', email])
            print("✓ Git user configured")
        else:
            print(f"✓ Git user already configured: {result.stdout.strip()}")
        
        # Set credential helper for Windows
        if sys.platform == 'win32':
            subprocess.run(['git', 'config', '--global', 'credential.helper', 'manager'])
            print("✓ Git credential helper configured")
        
        return True
    except Exception as e:
        print(f"⚠ Warning: Could not configure Git: {e}")
        print("You may need to configure Git manually")
        return True


def create_launch_scripts():
    """Create convenient launch scripts"""
    print_header("Creating Launch Scripts")
    
    # Windows batch file for GUI
    if sys.platform == 'win32':
        gui_script = Path(__file__).parent / "Wave.AI.bat"
        with open(gui_script, 'w') as f:
            f.write('@echo off\n')
            f.write('title Wave.AI - Free AI Coding Assistant\n')
            f.write(f'"{sys.executable}" "%~dp0main.py" gui\n')
            f.write('pause\n')
        print("✓ Created: Wave.AI.bat (GUI launcher)")
        
        # Windows batch file for CLI
        cli_script = Path(__file__).parent / "Wave.AI-CLI.bat"
        with open(cli_script, 'w') as f:
            f.write('@echo off\n')
            f.write('title Wave.AI CLI\n')
            f.write(f'"{sys.executable}" "%~dp0wave-ai.py" %*\n')
        print("✓ Created: Wave.AI-CLI.bat (CLI launcher)")
    
    return True


def run_initial_config():
    """Run initial configuration wizard"""
    print_header("Initial Configuration")
    
    print("Would you like to configure Wave.AI now?")
    print("You can also run 'python wave-ai.py init' later.")
    response = input("\nRun configuration wizard? (y/n): ").strip().lower()
    
    if response == 'y':
        try:
            from src.cli.commands import cli
            sys.argv = ['wave-ai.py', 'init']
            cli()
        except Exception as e:
            print(f"⚠ Could not run configuration wizard: {e}")
            print("You can run it manually later with: python wave-ai.py init")
    
    return True


def print_completion_message():
    """Print completion message with next steps"""
    print_header("Setup Complete!")
    
    print("🎉 Wave.AI has been set up successfully!\n")
    print("Next Steps:\n")
    print("1. Configure Wave.AI:")
    print("   python wave-ai.py init\n")
    print("2. Start Wave.AI:")
    print("   GUI Mode: python main.py gui")
    print("   CLI Mode: python wave-ai.py start\n")
    
    if sys.platform == 'win32':
        print("   Or double-click: Wave.AI.bat\n")
    
    print("3. Connect Perplexity to GitHub:")
    print("   - Go to https://www.perplexity.ai")
    print("   - Sign in and go to Settings → Integrations")
    print("   - Connect your GitHub account\n")
    print("4. Read the documentation:")
    print("   README.md - User guide")
    print("   ARCHITECTURE.md - Technical details\n")
    print("For help, run: python wave-ai.py --help\n")
    print("Happy coding! 🌊")


def main():
    """Main setup routine"""
    print_header("Wave.AI Setup")
    print("Welcome to Wave.AI - Free AI Coding Assistant")
    print("This setup will install dependencies and configure your environment.\n")
    
    # Run setup steps
    steps = [
        ("Checking Python version", check_python_version),
        ("Checking Git installation", check_git_installed),
        ("Creating directories", create_directories),
        ("Installing dependencies", install_dependencies),
        ("Configuring Git", configure_git),
        ("Creating launch scripts", create_launch_scripts),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            print("Please fix the errors and run setup.py again.")
            return False
    
    # Optional configuration
    run_initial_config()
    
    # Print completion message
    print_completion_message()
    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

