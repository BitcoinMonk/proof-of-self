#!/bin/bash
# Start Proof-of-Monk MCP Server

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH="$HOME/repos/proof-of-monk/src"
export PROOF_OF_MONK_DB="$HOME/repos/proof-of-monk/tests/test.db"

# Start server
echo "Starting Proof-of-Monk MCP Server..."
echo "Database: $PROOF_OF_MONK_DB"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 src/proof_of_monk/server.py
