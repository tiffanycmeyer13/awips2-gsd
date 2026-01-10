#!/usr/bin/env python3
"""
Replace every integer id in an SQL INSERT statement with sequential IDs
starting from a base value provided on the command line.

Usage:
    python replace_ids.py input.sql output.sql 1000
This will make the first row id = 1000, the next = 1001, etc.
"""

import re
import sys

def replace_ids(infile, outfile, base_id):
    with open(infile, "r", encoding="utf-8") as f:
        text = f.read()

    current_id = base_id

    def repl(match):
        nonlocal current_id
        replacement = f"({current_id},"
        current_id += 1
        return replacement

    # Replace every "( number ," with "( <new_id> ,"
    pattern = r"\(\s*\d+\s*,"
    new_text, count = re.subn(pattern, repl, text)

    with open(outfile, "w", encoding="utf-8") as f:
        f.write(new_text)

    print(f"Replaced {count} ids. Wrote output to {outfile}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python replace_ids.py input.sql output.sql base_id")
    else:
        infile, outfile, base_id_str = sys.argv[1], sys.argv[2], sys.argv[3]
        try:
            base_id = int(base_id_str)
        except ValueError:
            sys.exit("Error: base_id must be an integer")
        replace_ids(infile, outfile, base_id)

