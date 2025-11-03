"""
Wave.AI - Free AI Coding Assistant
Main entry point for the application
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.utils.logger import logger
from src.core.config_manager import config


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Wave.AI - Free AI Coding Assistant powered by Perplexity',
        epilog='For more information, see README.md'
    )
    
    parser.add_argument(
        'mode',
        nargs='?',
        choices=['gui', 'cli'],
        default='gui',
        help='Launch mode: gui (default) or cli'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Wave.AI 1.0.0'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom configuration file'
    )
    
    args = parser.parse_args()
    
    # Load custom config if specified
    if args.config:
        try:
            config.import_config(args.config)
            logger.info(f"Loaded configuration from: {args.config}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)
    
    # Launch in appropriate mode
    if args.mode == 'gui':
        logger.info("Starting Wave.AI in GUI mode")
        from src.gui.main_window import start_gui
        start_gui()
    else:
        logger.info("Starting Wave.AI in CLI mode")
        from src.cli.commands import cli
        cli()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Wave.AI interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)

