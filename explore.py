#!/usr/bin/env python3
"""Explore the codex by sending commands and capturing output."""
import subprocess
import sys

def run_codex(commands_str, timeout=300):
    """Run codex with given commands after the decryption key."""
    key = '(\\b.bb)(\\v.vv)06FHPVboundvarHRAk\n'
    input_data = (key + commands_str).encode('latin-1')

    proc = subprocess.Popen(
        ['./target/release/um', 'codex.umz'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        stdout, stderr = proc.communicate(input=input_data, timeout=timeout)
        return stdout
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, _ = proc.communicate()
        return stdout

def extract_um_program(raw_output):
    """Extract the UM program bytes after 'UM program follows colon:'"""
    marker = b'UM program follows colon:'
    idx = raw_output.find(marker)
    if idx == -1:
        return None
    return raw_output[idx + len(marker):]

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'explore'

    if mode == 'explore':
        # Just send 'p' and see what we get
        cmds = sys.argv[2] if len(sys.argv) > 2 else 'p\n'
        raw = run_codex(cmds)
        # Show printable parts
        text = raw.decode('latin-1', errors='replace')
        # Print first 5000 chars, filtering control chars
        filtered = ''.join(c if (c.isprintable() or c in '\n\r\t') else '.' for c in text[:10000])
        print(filtered)

    elif mode == 'dump':
        # Extract the UM program and save to file
        outfile = sys.argv[2] if len(sys.argv) > 2 else 'extracted.um'
        raw = run_codex('p\n')
        program = extract_um_program(raw)
        if program:
            with open(outfile, 'wb') as f:
                f.write(program)
            print(f"Extracted {len(program)} bytes to {outfile}")
        else:
            print("Could not find UM program marker")

    elif mode == 'text':
        # Show all text output with given commands
        cmds = sys.argv[2] if len(sys.argv) > 2 else ''
        raw = run_codex(cmds)
        text = raw.decode('latin-1', errors='replace')
        # Only show printable lines
        for line in text.split('\n'):
            cleaned = ''.join(c if (c.isprintable() or c == '\t') else '' for c in line).strip()
            if cleaned:
                print(cleaned)
