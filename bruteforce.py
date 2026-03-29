#!/usr/bin/env python3
"""Fast brute force password cracker for UMIX."""
import subprocess
import sys
import concurrent.futures

WORDS = [
    "airplane", "alphabet", "aviator", "bidirectional", "changeme",
    "creosote", "cyclone", "december", "dolphin", "elephant",
    "ersatz", "falderal", "functional", "future", "guitar",
    "gymnast", "hello", "imbroglio", "january", "joshua",
    "kernel", "kingfish", "(\\b.bb)(\\v.vv)", "millennium", "monday",
    "nemesis", "oatmeal", "october", "paladin", "pass",
    "password", "penguin", "polynomial", "popcorn", "qwerty",
    "sailor", "swordfish", "symmetry", "system", "tattoo",
    "thursday", "tinman", "topography", "unicorn", "vader",
    "vampire", "viper", "warez", "xanadu", "xyzzy",
    "zephyr", "zeppelin", "zxcvbnm",
]

USERS = ["knr", "yang", "gardener", "hmonk", "bbarker", "ftd"]

def try_login(user, pwd):
    """Try logging in with given credentials. Returns True if successful."""
    input_data = f"{user}\n{pwd}\n".encode('latin-1')
    proc = subprocess.Popen(
        ['./target/release/um', 'extracted.um'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        stdout, _ = proc.communicate(input=input_data, timeout=15)
        output = stdout.decode('latin-1', errors='replace')
        return "logged in" in output
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        return False

def crack_user(user):
    """Try all password combinations for a user."""
    # First try plain words
    for word in WORDS:
        if try_login(user, word):
            return (user, word)

    # Then try word+DD
    for word in WORDS:
        for num in range(100):
            pwd = f"{word}{num:02d}"
            if try_login(user, pwd):
                return (user, pwd)

    return (user, None)

if __name__ == '__main__':
    users = sys.argv[1:] if len(sys.argv) > 1 else USERS

    for user in users:
        print(f"Cracking {user}...", flush=True)
        result = crack_user(user)
        if result[1]:
            print(f"SUCCESS: {result[0]} / {result[1]}")
        else:
            print(f"FAILED: {result[0]}")
