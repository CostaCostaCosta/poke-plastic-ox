#!/usr/bin/env python3
"""Emit only the region patch, preserving independent story-generator edits."""
import difflib
from pathlib import Path
from region_v7 import apply_region

changes = {}
def read(path):
    return changes.get(path, Path(path).read_text() if Path(path).exists() else '')
def put(path, value):
    changes[path] = value

apply_region(read, put)
print('*** Begin Patch')
for path, value in changes.items():
    old = Path(path).read_text() if Path(path).exists() else ''
    if old == value:
        continue
    if not Path(path).exists():
        print('*** Add File: '+path)
        print(''.join('+'+line for line in value.splitlines(True)), end='')
    else:
        print('*** Update File: '+path)
        for line in list(difflib.unified_diff(old.splitlines(True), value.splitlines(True)))[2:]:
            print('@@' if line.startswith('@@') else line, end='\n' if line.startswith('@@') else '')
print('*** End Patch')
