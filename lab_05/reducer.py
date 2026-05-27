#!/usr/bin/env python3
import sys
from collections import defaultdict

def reduce_function():
    word_count = defaultdict(int)
    for line in sys.stdin:
        word, count = line.strip().split('\t')
        word_count[word] += int(count)
    
    for word, count in sorted(word_count.items(), key=lambda x: x[1], reverse=True):
        print(f"{word}\t{count}")

if __name__ == "__main__":
    reduce_function()
