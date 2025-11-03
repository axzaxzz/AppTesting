"""
CLI Interface for Wave.AI
Provides command-line controls for the sync engine
"""

import click
import sys
from pathlib import Path
from colorama import init, Fore, Style
from datetime import datetime

# Initialize colorama for Windows color support
init(autoreset=True)

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.core.sync_engine import sync_engine
from src.core.config_manager import config
from src.utils.logger import logger


def print_success(message):
    """Print success message in green"""
    click.echo(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message):
    """Print error message in red"""
    click.echo(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_info(message):
    """Print info message in blue"""
    click.echo(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")


def print_warning(message):
    """Print warning message in yellow"""
    click.echo(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")


@click.group()
@click.version_option(version='1.0.0', prog_name='Wave.AI')
def cli():
    """
    Wave.AI - Free AI Coding Assistant
    
    A lightweight IDE powered by Perplexity's GitHub connector
    """
    pass


@cli.command()
def start():
    """Start the synchronization engine"""
    print_info("Starting Wave.AI sync engine...")
    
    # Initialize if needed
    if not sync_engine.git_sync:
        success, message = sync_engine.initialize()
        if not success:
            print_error(f"Initialization failed: {message}")
            return
    
    # Start sync engine
    success, message = sync_engine.start()
    if success:
        print_success(message)
        print_info(f"Syncing: {config.get('github.repo_url')}")
        print_info(f"Local directory: {config.get('local.code_directory')}")
        print_info(f"Sync interval: {config.get('github.sync_interval')}s")
        print_info("Press Ctrl+C to stop (or use 'wave-ai stop')")
    else:
        print_error(message)


@cli.command()
def stop():
    """Stop the synchronization engine"""
    print_info("Stopping Wave.AI sync engine...")
    
    success, message = sync_engine.stop()
    if success:
        print_success(message)
    else:
        print_error(message)


@cli.command()
def status():
    """Show current synchronization status"""
    status_data = sync_engine.get_status()
    
    click.echo(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    click.echo(f"{Fore.CYAN}Wave.AI Status{Style.RESET_ALL}")
    click.echo(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")
    
    # Engine status
    if status_data['is_running']:
        click.echo(f"Status: {Fore.GREEN}Running ●{Style.RESET_ALL}")
    else:
        click.echo(f"Status: {Fore.RED}Stopped ○{Style.RESET_ALL}")
    
    # Configuration
    click.echo(f"\n{Fore.YELLOW}Configuration:{Style.RESET_ALL}")
    click.echo(f"  Repository: {status_data['config']['repo_url']}")
    click.echo(f"  Local Dir:  {status_data['config']['local_dir']}")
    click.echo(f"  Auto-pull:  {status_data['config']['auto_pull']}")
    click.echo(f"  Auto-push:  {status_data['config']['auto_push']}")
    
    # Git status
    if 'git_status' in status_data and 'latest_commit' in status_data['git_status']:
        git_status = status_data['git_status']
        click.echo(f"\n{Fore.YELLOW}Git Status:{Style.RESET_ALL}")
        click.echo(f"  Branch:     {git_status['current_branch']}")
        
        latest = git_status['latest_commit']
        if latest:
            click.echo(f"  Last Commit: {latest['hash']} - {latest['message'][:50]}")
            click.echo(f"  Author:     {latest['author']}")
            click.echo(f"  Date:       {latest['date']}")
        
        if git_status['is_dirty']:
            click.echo(f"  {Fore.YELLOW}Uncommitted changes:{Style.RESET_ALL} {len(git_status['changed_files'])} file(s)")
    
    # Statistics
    stats = status_data['stats']
    click.echo(f"\n{Fore.YELLOW}Statistics:{Style.RESET_ALL}")
    click.echo(f"  Pulls:      {stats['pulls']}")
    click.echo(f"  Pushes:     {stats['pushes']}")
    click.echo(f"  Conflicts:  {stats['conflicts']}")
    click.echo(f"  Errors:     {stats['errors']}")
    
    if stats['last_activity']:
        click.echo(f"  Last Activity: {stats['last_activity']}")
    
    # Version control
    if 'version_control' in status_data and status_data['version_control']:
        vc_info = status_data['version_control']
        click.echo(f"\n{Fore.YELLOW}Version Control:{Style.RESET_ALL}")
        click.echo(f"  Current: {vc_info['description']}")
        click.echo(f"  Can revert: {vc_info['steps_back_available']} step(s)")
        click.echo(f"  Can forward: {vc_info['steps_forward_available']} step(s)")
    
    click.echo(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")


@cli.command()
@click.option('--steps', '-s', default=1, help='Number of steps to revert')
def revert(steps):
    """Revert to a previous version"""
    print_info(f"Reverting {steps} step(s)...")
    
    if not sync_engine.version_control:
        print_error("Version control not initialized")
        return
    
    success, message = sync_engine.version_control.revert(steps)
    if success:
        print_success(message)
    else:
        print_error(message)


@cli.command()
@click.option('--steps', '-s', default=1, help='Number of steps to move forward')
def forward(steps):
    """Move forward to a newer version"""
    print_info(f"Moving forward {steps} step(s)...")
    
    if not sync_engine.version_control:
        print_error("Version control not initialized")
        return
    
    success, message = sync_engine.version_control.forward(steps)
    if success:
        print_success(message)
    else:
        print_error(message)


@cli.command()
def history():
    """Show version history"""
    if not sync_engine.version_control:
        print_error("Version control not initialized")
        return
    
    history_data = sync_engine.version_control.get_history_summary(max_items=20)
    
    if not history_data:
        print_info("No version history available")
        return
    
    click.echo(f"\n{Fore.CYAN}Version History (most recent 20):{Style.RESET_ALL}\n")
    
    for item in reversed(history_data):
        marker = "→" if item['is_current'] else " "
        color = Fore.GREEN if item['is_current'] else Fore.WHITE
        
        click.echo(f"{color}{marker} [{item['id']}] {item['commit_hash']} - {item['description']}{Style.RESET_ALL}")
        click.echo(f"    {item['timestamp']}\n")


@cli.command()
@click.argument('checkpoint_id', type=int)
def goto(checkpoint_id):
    """Go to a specific checkpoint by ID"""
    print_info(f"Going to checkpoint {checkpoint_id}...")
    
    if not sync_engine.version_control:
        print_error("Version control not initialized")
        return
    
    success, message = sync_engine.version_control.goto_checkpoint(checkpoint_id)
    if success:
        print_success(message)
    else:
        print_error(message)


@cli.command()
@click.option('--description', '-d', help='Checkpoint description')
def checkpoint(description):
    """Create a manual checkpoint"""
    if not sync_engine.version_control:
        print_error("Version control not initialized")
        return
    
    desc = description or f"Manual checkpoint at {datetime.now().strftime('%H:%M:%S')}"
    success, checkpoint_id = sync_engine.version_control.create_checkpoint(desc)
    
    if success:
        print_success(f"Created checkpoint {checkpoint_id}: {desc}")
    else:
        print_error(checkpoint_id)


@cli.command()
def sync():
    """Manually trigger a sync operation"""
    print_info("Triggering manual sync...")
    
    if not sync_engine.git_sync:
        print_error("Sync engine not initialized")
        return
    
    success, message = sync_engine.manual_sync()
    if success:
        print_success(message)
    else:
        print_error(message)


@cli.command()
def pull():
    """Force pull from GitHub"""
    print_info("Pulling from GitHub...")
    
    if not sync_engine.git_sync:
        print_error("Sync engine not initialized")
        return
    
    success, message = sync_engine.force_pull()
    if success:
        print_success(message)
    else:
        print_error(message)


@cli.command()
def push():
    """Force push to GitHub"""
    print_info("Pushing to GitHub...")
    
    if not sync_engine.git_sync:
        print_error("Sync engine not initialized")
        return
    
    success, message = sync_engine.force_push()
    if success:
        print_success(message)
    else:
        print_error(message)


@cli.command()
def config_show():
    """Show current configuration"""
    click.echo(f"\n{Fore.CYAN}Wave.AI Configuration:{Style.RESET_ALL}\n")
    
    click.echo(f"{Fore.YELLOW}GitHub:{Style.RESET_ALL}")
    click.echo(f"  Repository URL: {config.get('github.repo_url')}")
    click.echo(f"  Branch: {config.get('github.branch')}")
    click.echo(f"  Auto-push: {config.get('github.auto_push')}")
    click.echo(f"  Auto-pull: {config.get('github.auto_pull')}")
    click.echo(f"  Sync Interval: {config.get('github.sync_interval')}s")
    
    click.echo(f"\n{Fore.YELLOW}Local:{Style.RESET_ALL}")
    click.echo(f"  Code Directory: {config.get('local.code_directory')}")
    click.echo(f"  Watch Patterns: {', '.join(config.get('local.watch_patterns'))}")
    
    click.echo(f"\n{Fore.YELLOW}UI:{Style.RESET_ALL}")
    click.echo(f"  Theme: {config.get('ui.theme')}")
    click.echo(f"  Max Tabs: {config.get('ui.max_tabs')}")
    
    click.echo()


@cli.command()
@click.argument('key')
@click.argument('value')
def config_set(key, value):
    """Set a configuration value (e.g., wave-ai config-set github.repo_url <url>)"""
    try:
        # Try to parse value as boolean or number
        if value.lower() in ['true', 'false']:
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
        
        config.set(key, value)
        print_success(f"Set {key} = {value}")
    except Exception as e:
        print_error(f"Failed to set config: {e}")


@cli.command()
def branches():
    """List all available branches"""
    if not sync_engine.git_sync:
        print_error("Sync engine not initialized")
        return
    
    branch_info = sync_engine.git_sync.get_all_branches()
    
    click.echo(f"\n{Fore.CYAN}Available Branches:{Style.RESET_ALL}\n")
    
    # Local branches
    click.echo(f"{Fore.YELLOW}Local Branches:{Style.RESET_ALL}")
    for branch in branch_info.get('local', []):
        marker = "→" if branch == branch_info.get('current') else " "
        color = Fore.GREEN if branch == branch_info.get('current') else Fore.WHITE
        click.echo(f"{color}{marker} {branch}{Style.RESET_ALL}")
    
    # Remote branches
    click.echo(f"\n{Fore.YELLOW}Remote Branches:{Style.RESET_ALL}")
    for branch in branch_info.get('remote', []):
        click.echo(f"  {branch}")
    
    click.echo()


@cli.command()
def init():
    """Interactive setup wizard"""
    click.echo(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    click.echo(f"{Fore.CYAN}Wave.AI Setup Wizard{Style.RESET_ALL}")
    click.echo(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")
    
    # Get GitHub repo URL
    repo_url = click.prompt(
        f"{Fore.YELLOW}GitHub Repository URL{Style.RESET_ALL}",
        default=config.get('github.repo_url', '')
    )
    config.set('github.repo_url', repo_url, save_immediately=False)
    
    # Get local directory
    local_dir = click.prompt(
        f"{Fore.YELLOW}Local Code Directory{Style.RESET_ALL}",
        default=config.get('local.code_directory', '')
    )
    config.set('local.code_directory', local_dir, save_immediately=False)
    
    # Get branch
    branch = click.prompt(
        f"{Fore.YELLOW}Git Branch{Style.RESET_ALL}",
        default=config.get('github.branch', 'main')
    )
    config.set('github.branch', branch, save_immediately=False)
    
    # Sync interval
    sync_interval = click.prompt(
        f"{Fore.YELLOW}Sync Interval (seconds){Style.RESET_ALL}",
        default=config.get('github.sync_interval', 30),
        type=int
    )
    config.set('github.sync_interval', sync_interval, save_immediately=False)
    
    # Save all config
    config.save()
    
    print_success("Configuration saved!")
    
    # Validate
    is_valid, errors = config.validate()
    if is_valid:
        print_success("Configuration is valid")
        
        # Ask to initialize
        if click.confirm(f"\n{Fore.YELLOW}Initialize sync engine now?{Style.RESET_ALL}"):
            success, message = sync_engine.initialize()
            if success:
                print_success(message)
            else:
                print_error(message)
    else:
        print_warning("Configuration has errors:")
        for error in errors:
            print_error(f"  - {error}")


if __name__ == '__main__':
    cli()

