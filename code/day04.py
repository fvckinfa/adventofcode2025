from __future__ import annotations
import sys
from collections import deque
from typing import List, Tuple, Set

DIRS = [(-1,-1),(-1,0),(-1,1),
        (0,-1),        (0,1),
        (1,-1),(1,0),(1,1)]

def parse_grid(text: str) -> List[str]:
    lines = [ln.rstrip("\n") for ln in text.splitlines() if ln.strip("\n") != ""]
    return lines

def count_accessible_initial(grid: List[str]) -> int:
    h = len(grid)
    w = len(grid[0]) if h else 0
    g = grid
    acc = 0
    for r in range(h):
        for c in range(w):
            if g[r][c] != "@":
                continue
            neigh = 0
            for dr, dc in DIRS:
                rr, cc = r + dr, c + dc
                if 0 <= rr < h and 0 <= cc < w and g[rr][cc] == "@":
                    neigh += 1
            if neigh < 4:
                acc += 1
    return acc

def total_removed(grid: List[str]) -> int:
    h = len(grid)
    w = len(grid[0]) if h else 0

    # store '@' as a set for O(1) membership and removals
    papers: Set[Tuple[int,int]] = set()
    for r in range(h):
        row = grid[r]
        for c in range(w):
            if row[c] == "@":
                papers.add((r, c))

    # neighbor counts
    neigh_cnt = {}
    for r, c in papers:
        cnt = 0
        for dr, dc in DIRS:
            rr, cc = r + dr, c + dc
            if (rr, cc) in papers:
                cnt += 1
        neigh_cnt[(r, c)] = cnt

    q = deque([pos for pos, cnt in neigh_cnt.items() if cnt < 4])
    removed = 0

    while q:
        pos = q.popleft()
        if pos not in papers:
            continue
        if neigh_cnt[pos] >= 4:
            continue

        # remove it
        papers.remove(pos)
        removed += 1
        r, c = pos

        # update neighbors
        for dr, dc in DIRS:
            nb = (r + dr, c + dc)
            if nb in papers:
                neigh_cnt[nb] -= 1
                if neigh_cnt[nb] < 4:
                    q.append(nb)

    return removed

def main() -> None:
    text = sys.stdin.read()
    grid = parse_grid(text)
    print(count_accessible_initial(grid))
    print(total_removed(grid))

if __name__ == "__main__":
    main()
