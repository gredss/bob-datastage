#!/usr/bin/env python3
"""
Wrapper script to run DataStage MCP Server with workspace directory support.
This script captures the current working directory before changing to the server directory.
"""

import os
import sys
from pathlib import Path

# Capture the workspace directory (where this script is called from)
workspace_dir = Path.cwd()

# Set environment variable for the server to use
os.environ['WORKSPACE_DIR'] = str(workspace_dir)

# Change to the server directory
server_dir = Path(__file__).parent
os.chdir(server_dir)

# Now run the server
from src.server import main

if __name__ == '__main__':
    main()

# Made with Bob
