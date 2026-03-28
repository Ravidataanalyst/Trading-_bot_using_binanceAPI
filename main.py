#!/usr/bin/env python3
"""
Main entry point for the Binance Futures Testnet Trading Bot.

This script provides a command-line interface for placing orders on Binance Futures Testnet.
"""

import sys
import os

# Add the bot directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bot'))

from bot.cli import main

if __name__ == '__main__':
    main()
