#!/usr/bin/env python3
"""Interactive wrapper for the UM codex."""
import subprocess
import sys
import select
import os
import time

def run_um(commands, timeout=120, binary_dump=None):
    """Run the UM with a sequence of commands, capturing output."""
    key = '(\\b.bb)(\\v.vv)06FHPVboundvarHRAk\n'

    proc = subprocess.Popen(
        ['./target/release/um', 'codex.umz'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Send key + commands
    input_data = key + commands + '\n'
    try:
        stdout, stderr = proc.communicate(input=input_data.encode('latin-1'), timeout=timeout)
        output = stdout.decode('latin-1', errors='replace')
        if binary_dump:
            with open(binary_dump, 'wb') as f:
                f.write(stdout)
        return output
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, _ = proc.communicate()
        output = stdout.decode('latin-1', errors='replace')
        if binary_dump:
            with open(binary_dump, 'wb') as f:
                f.write(stdout)
        return output

if __name__ == '__main__':
    cmds = sys.argv[1] if len(sys.argv) > 1 else 'p\n'
    print(run_um(cmds)[:10000])
