"""
Wave.AI CLI Wrapper
Convenient command-line interface for Wave.AI
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.cli.commands import cli

if __name__ == '__main__':
    cli()

