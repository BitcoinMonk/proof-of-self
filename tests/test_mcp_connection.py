#!/usr/bin/env python3
"""Test MCP server connection by sending an initialize message."""
import asyncio
import json
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_mcp():
    """Send a test initialize message to the MCP server."""
    # Start the server as a subprocess
    import subprocess

    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parent / "src")
    env["PROOF_OF_MONK_DB"] = str(Path(__file__).parent / "tests" / "test.db")

    proc = await asyncio.create_subprocess_exec(
        str(Path(__file__).parent / "venv" / "bin" / "python3"),
        str(Path(__file__).parent / "src" / "proof_of_self" / "server.py"),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )

    # Send an initialize request
    initialize_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }

    message = json.dumps(initialize_request) + "\n"
    print(f"Sending: {message}", file=sys.stderr)

    proc.stdin.write(message.encode())
    await proc.stdin.drain()

    # Read response with timeout
    try:
        response_bytes = await asyncio.wait_for(proc.stdout.readline(), timeout=5.0)
        response = response_bytes.decode().strip()
        print(f"Received: {response}", file=sys.stderr)

        # Try to parse as JSON
        response_json = json.loads(response)
        print(f"✓ Server responded with valid JSON", file=sys.stderr)
        print(json.dumps(response_json, indent=2))

    except asyncio.TimeoutError:
        print("✗ Timeout waiting for response", file=sys.stderr)
        stderr = await proc.stderr.read()
        print(f"stderr: {stderr.decode()}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON response: {e}", file=sys.stderr)
        print(f"Raw response: {response}", file=sys.stderr)
        return 1
    finally:
        proc.terminate()
        await proc.wait()

    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(test_mcp()))
