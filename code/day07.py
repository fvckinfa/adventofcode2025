from __future__ import annotations

import sys
import bisect
from collections import deque


def parse(lines: list[str]) -> tuple[int, int, int, dict[int, list[int]]]:
	height = len(lines)
	width = len(lines[0]) if height else 0
	start_row = start_col = -1
	cols: dict[int, list[int]] = {}

	for r, line in enumerate(lines):
		for c, ch in enumerate(line):
			if ch == "S":
				start_row, start_col = r, c
			elif ch == "^":
				cols.setdefault(c, []).append(r)

	for c in cols:
		cols[c].sort()

	if start_row == -1:
		raise ValueError("Start S not found")

	return start_row, start_col, width, cols


def count_splits(lines: list[str]) -> int:
	start_row, start_col, width, cols = parse(lines)
	splits = 0
	seen: set[tuple[int, int]] = set()
	split_seen: set[tuple[int, int]] = set()
	q: deque[tuple[int, int]] = deque([(start_row, start_col)])

	while q:
		row, col = q.popleft()
		if not (0 <= col < width and 0 <= row < len(lines)):
			continue
		if (row, col) in seen:
			continue
		seen.add((row, col))

		col_rows = cols.get(col)
		if not col_rows:
			continue

		idx = bisect.bisect_left(col_rows, row)

		if idx < len(col_rows) and col_rows[idx] == row:
			split_pos = (row, col)
			if split_pos not in split_seen:
				split_seen.add(split_pos)
				splits += 1
				q.append((row, col - 1))
				q.append((row, col + 1))
			continue

		if idx < len(col_rows):
			split_row = col_rows[idx]
			split_pos = (split_row, col)
			if split_pos not in split_seen:
				split_seen.add(split_pos)
				splits += 1
				q.append((split_row, col - 1))
				q.append((split_row, col + 1))

	return splits


def count_timelines(lines: list[str]) -> int:
	start_row, start_col, width, cols = parse(lines)

	inflow: dict[tuple[int, int], int] = {(start_row, start_col): 1}
	q: deque[tuple[int, int]] = deque([(start_row, start_col)])
	exit_count = 0

	while q:
		row, col = q.popleft()
		cnt = inflow.pop((row, col), 0)
		if cnt == 0:
			continue
		if not (0 <= col < width and 0 <= row < len(lines)):
			exit_count += cnt
			continue

		col_rows = cols.get(col)
		if not col_rows:
			exit_count += cnt
			continue

		idx = bisect.bisect_left(col_rows, row)

		# Splitter at current position: branch left/right.
		if idx < len(col_rows) and col_rows[idx] == row:
			for ncol in (col - 1, col + 1):
				if 0 <= ncol < width:
					key = (row, ncol)
					inflow[key] = inflow.get(key, 0) + cnt
					if key not in q:
						q.append(key)
				else:
					exit_count += cnt
			continue

		# Next splitter below current position.
		if idx < len(col_rows):
			split_row = col_rows[idx]
			key = (split_row, col)
			inflow[key] = inflow.get(key, 0) + cnt
			if key not in q:
				q.append(key)
			continue

		# No splitter below: exits manifold.
		exit_count += cnt

	return exit_count


def main() -> None:
	lines = sys.stdin.read().splitlines()
	if "--part2" in sys.argv:
		print(count_timelines(lines))
	else:
		print(count_splits(lines))


if __name__ == "__main__":
	main()
