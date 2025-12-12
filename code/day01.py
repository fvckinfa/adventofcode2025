#!/usr/bin/env python3
import sys

MOD = 100

def parse(data: str):
    ops = []
    for line in data.splitlines():
        line = line.strip()
        if not line:
            continue
        d = line[0]
        n = int(line[1:])
        if d not in ("L", "R"):
            raise ValueError(f"Bad direction: {line}")
        ops.append((d, n))
    return ops

def part1(ops):
    pos = 50
    hits = 0
    for d, n in ops:
        if d == "R":
            pos = (pos + n) % MOD
        else:
            pos = (pos - n) % MOD
        if pos == 0:
            hits += 1
    return hits

def zeros_during_rotation(pos, d, dist):
    """Count of k in [1..dist] such that (pos + step*k) % 100 == 0."""
    if dist <= 0:
        return 0

    step = 1 if d == "R" else -1

    # First time we land on 0 (t in 1..100)
    # R: need k ≡ -pos (mod 100)
    # L: need k ≡ pos (mod 100)
    if step == 1:
        t = (-pos) % MOD
    else:
        t = pos % MOD
    if t == 0:
        t = MOD  # from 0, you hit 0 again after 100 clicks

    if dist < t:
        return 0
    return 1 + (dist - t) // MOD

def part2(ops):
    pos = 50
    hits = 0
    for d, n in ops:
        hits += zeros_during_rotation(pos, d, n)
        step = 1 if d == "R" else -1
        pos = (pos + step * n) % MOD
    return hits

if __name__ == "__main__":
    data = sys.stdin.read()
    ops = parse(data)
    print(part1(ops))
    print(part2(ops))
