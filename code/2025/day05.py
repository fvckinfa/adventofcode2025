from __future__ import annotations
import sys
from bisect import bisect_right
from typing import List, Tuple
from utils import merge_intervals, union_size

Interval = Tuple[int, int]

def parse_day5(text: str) -> tuple[List[Interval], List[int]]:
    # ranges, blank line, ids
    parts = text.strip("\n").split("\n\n")
    if len(parts) < 1:
        return [], []
    ranges_part = parts[0].strip()
    ids_part = parts[1].strip() if len(parts) >= 2 else ""

    intervals: List[Interval] = []
    for ln in ranges_part.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        a, b = ln.split("-")
        intervals.append((int(a), int(b)))

    ids: List[int] = []
    for ln in ids_part.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        ids.append(int(ln))

    return intervals, ids

def is_in_union(merged: List[Interval], x: int) -> bool:
    # merged sorted by start; find rightmost interval with start <= x
    starts = [a for a, _ in merged]
    i = bisect_right(starts, x) - 1
    if i < 0:
        return False
    a, b = merged[i]
    return a <= x <= b

def main() -> None:
    text = sys.stdin.read()
    intervals, ids = parse_day5(text)

    merged = merge_intervals(intervals)

    # Part 1: count available IDs that are fresh
    cnt = 0
    for x in ids:
        if is_in_union(merged, x):
            cnt += 1

    # Part 2: total number of fresh IDs considered fresh (size of union)
    total = union_size(merged)

    print(cnt)
    print(total)

if __name__ == "__main__":
    main()
