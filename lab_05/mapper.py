#!/usr/bin/env python3
import sys
import re

def map_function(text):
    words = re.findall(r'\b\w+\b', text.lower())
    for word in words:
        print(f"{word}\t1")

if __name__ == "__main__":
    for line in sys.stdin:
        map_function(line)
