from __future__ import annotations

import sys
from typing import List, Tuple


def parse_points(lines: List[str]) -> List[Tuple[int, int, int]]:
	pts: List[Tuple[int, int, int]] = []
	for line in lines:
		if not line.strip():
			continue
		x_str, y_str, z_str = line.strip().split(",")
		pts.append((int(x_str), int(y_str), int(z_str)))
	return pts


def k_shortest_edges(points: List[Tuple[int, int, int]], k: int) -> List[Tuple[int, int, int]]:
	"""Return the first k edges (dist2, i, j) sorted by increasing distance squared."""

	edges: List[Tuple[int, int, int]] = []
	n = len(points)
	for i in range(n):
		xi, yi, zi = points[i]
		for j in range(i + 1, n):
			xj, yj, zj = points[j]
			dx = xi - xj
			dy = yi - yj
			dz = zi - zj
			dist2 = dx * dx + dy * dy + dz * dz
			edges.append((dist2, i, j))

	edges.sort(key=lambda t: t[0])
	return edges[:k]


class DSU:
	def __init__(self, n: int) -> None:
		self.parent = list(range(n))
		self.size = [1] * n

	def find(self, x: int) -> int:
		while self.parent[x] != x:
			self.parent[x] = self.parent[self.parent[x]]
			x = self.parent[x]
		return x

	def union(self, a: int, b: int) -> None:
		ra, rb = self.find(a), self.find(b)
		if ra == rb:
			return
		if self.size[ra] < self.size[rb]:
			ra, rb = rb, ra
		self.parent[rb] = ra
		self.size[ra] += self.size[rb]


def last_merge_product(lines: List[str]) -> int:
	points = parse_points(lines)
	n = len(points)
	if n == 0:
		return 0

	edges: List[Tuple[int, int, int]] = []
	for i in range(n):
		xi, yi, zi = points[i]
		for j in range(i + 1, n):
			xj, yj, zj = points[j]
			dx = xi - xj
			dy = yi - yj
			dz = zi - zj
			dist2 = dx * dx + dy * dy + dz * dz
			edges.append((dist2, i, j))

	edges.sort(key=lambda t: t[0])

	dsu = DSU(n)
	components = n
	for _, i, j in edges:
		ri, rj = dsu.find(i), dsu.find(j)
		if ri == rj:
			continue
		dsu.union(ri, rj)
		components -= 1
		if components == 1:
			xi, _, _ = points[i]
			xj, _, _ = points[j]
			return xi * xj

	return 0


def solve(lines: List[str], k: int) -> int:
	points = parse_points(lines)
	n = len(points)
	if n == 0:
		return 0

	edges = k_shortest_edges(points, k)

	dsu = DSU(n)
	for _, i, j in edges:
		dsu.union(i, j)

	comp_sizes = {}
	for i in range(n):
		root = dsu.find(i)
		comp_sizes[root] = dsu.size[root]

	top3 = sorted(comp_sizes.values(), reverse=True)[:3]
	if len(top3) < 3:
		return 0
	return top3[0] * top3[1] * top3[2]


def main() -> None:
	lines = sys.stdin.read().splitlines()
	if "--part2" in sys.argv:
		print(last_merge_product(lines))
	else:
		# Part 1: connect the 1000 shortest pairs.
		print(solve(lines, 1000))


if __name__ == "__main__":
	main()
