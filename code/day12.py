from os import environ
import sys

# Increase recursion depth for deep backtracking on large grids
sys.setrecursionlimit(20000)


def parse_input(lines):
    shapes, grids, current_id = {}, [], -1
    for line in lines:
        if not (line := line.strip()):
            continue
        if "x" in line and ":" in line:
            dims, counts = line.split(":")
            grids.append((*map(int, dims.split("x")), list(map(int, counts.split()))))
        elif line.endswith(":"):
            current_id = int(line[:-1])
            shapes[current_id] = []
        else:
            val = sum((c == "#") << (len(line) - 1 - i) for i, c in enumerate(line))
            shapes[current_id].append((val, len(line)))
    return shapes, grids


def generate_variations(base_shapes):
    # All unique rotations and flips for each shape, as bitmasks
    variations = {}

    for sid, rows in base_shapes.items():
        max_w = max(r[1] for r in rows)
        matrix = []
        for val, w in rows:
            row_bits = [(val >> (w - 1 - i)) & 1 for i in range(max_w)]
            matrix.append(row_bits)

        seen_hashes = set()
        shape_vars = []

        # Try all orientations: 2 flips * 4 rotations
        current = matrix
        for _ in range(2):
            for _ in range(4):
                # Trim bounding box (remove empty rows/cols)
                min_r, max_r = len(current), -1
                min_c, max_c = len(current[0]), -1
                has_bits = False

                for r in range(len(current)):
                    for c in range(len(current[0])):
                        if current[r][c]:
                            has_bits = True
                            min_r, max_r = min(min_r, r), max(max_r, r)
                            min_c, max_c = min(min_c, c), max(max_c, c)

                if has_bits:
                    # Convert trimmed matrix back to integer bitmasks
                    trimmed_h = max_r - min_r + 1
                    trimmed_w = max_c - min_c + 1
                    int_rows = []
                    for r in range(min_r, max_r + 1):
                        r_val = 0
                        for c in range(min_c, max_c + 1):
                            r_val = (r_val << 1) | current[r][c]
                        int_rows.append(r_val)

                    # Store unique variations
                    sig = tuple(int_rows)
                    if sig not in seen_hashes:
                        seen_hashes.add(sig)
                        shape_vars.append((trimmed_h, trimmed_w, int_rows))

                # Rotate 90 deg clockwise
                h, w = len(current), len(current[0])
                current = [[current[h - 1 - r][c] for r in range(h)] for c in range(w)]

            # Flip vertically
            current = current[::-1]

        # Optimization: sort variations by height (tallest first helps column filling)
        shape_vars.sort(key=lambda x: -x[0])
        variations[sid] = shape_vars

    return variations


def is_space_sufficient(grid, width, height, required_area, min_item_area, slack=20):
    """
    Checks if grid has enough connected free space; skips expensive BFS if slack is high
    """
    used_area = sum(bin(row).count("1") for row in grid)
    free_area = (width * height) - used_area

    if free_area < required_area:
        return False

    # Skip connectivity check if plenty of space remains
    if free_area > required_area + slack:
        return True

    # Floodffill to calculate usable connected area
    visited = set()
    usable_free_area = 0

    # Map occupied cells for BFS
    collision = set()
    for r in range(height):
        row_val = grid[r]
        if row_val == 0:
            continue
        for c in range(width):
            if (row_val >> (width - 1 - c)) & 1:
                collision.add((r, c))

    for r in range(height):
        for c in range(width):
            if (r, c) not in collision and (r, c) not in visited:
                # Found a new empty island
                q = [(r, c)]
                visited.add((r, c))
                island_size = 0
                idx = 0
                while idx < len(q):
                    curr_r, curr_c = q[idx]
                    idx += 1
                    island_size += 1

                    for nr, nc in ((curr_r + 1, curr_c), (curr_r - 1, curr_c), (curr_r, curr_c + 1), (curr_r, curr_c - 1)):
                        if 0 <= nr < height and 0 <= nc < width:
                            if (nr, nc) not in collision and (nr, nc) not in visited:
                                visited.add((nr, nc))
                                q.append((nr, nc))

                # Pruning: Only count island if it fits the smallest remaining item
                if island_size >= min_item_area:
                    usable_free_area += island_size

                if usable_free_area >= required_area:
                    return True

    return usable_free_area >= required_area


def solve_recursive(grid, items, item_idx, width, height, variations, min_global_area):
    if item_idx == len(items):
        return True

    item = items[item_idx]
    sid = item["id"]

    # Pruning: Check if grid state allows fitting remaining items
    remaining_area_needed = sum(it["area"] for it in items[item_idx:])
    if not is_space_sufficient(grid, width, height, remaining_area_needed, min_global_area):
        return False

    # Symmetry breaking: if current item is identical to previous,
    # force placement to start after previous item's position
    start_r, start_c = 0, 0
    if item_idx > 0 and items[item_idx - 1]["id"] == sid:
        start_r, start_c = items[item_idx - 1]["placed_r"], items[item_idx - 1]["placed_c"]

    for h_var, w_var, rows in variations[sid]:
        # Iterate over valid grid positions
        for r in range(start_r, height - h_var + 1):
            c_begin = start_c if r == start_r else 0
            c_limit = width - w_var + 1

            for c in range(c_begin, c_limit):
                # 1 - collision check (bitwise)
                fits = True
                shift = width - c - w_var

                for i in range(h_var):
                    if grid[r + i] & (rows[i] << shift):
                        fits = False
                        break

                if fits:
                    # 2 - place shape
                    for i in range(h_var):
                        grid[r + i] |= rows[i] << shift

                    # Record placement for next item's symmetry check
                    item["placed_r"], item["placed_c"] = r, c

                    # 3 - recurse
                    if solve_recursive(grid, items, item_idx + 1, width, height, variations, min_global_area):
                        return True

                    # 4 - backtrack (remove shape)
                    for i in range(h_var):
                        grid[r + i] ^= rows[i] << shift

    return False


def part1(lines):
    shapes, queries = parse_input(lines)
    variations = generate_variations(shapes)

    # Pre-calculate areas for all shapes
    shape_areas = {sid: sum(bin(r).count("1") for r in vars[0][2]) for sid, vars in variations.items()}

    valid_count = 0

    for width, height, counts in queries:
        # Construct flat list of items to place
        items = []
        for sid, count in enumerate(counts):
            if count > 0:
                area = shape_areas[sid]
                for _ in range(count):
                    items.append({"id": sid, "area": area, "placed_r": 0, "placed_c": 0})

        if not items:
            valid_count += 1
            continue

        # Heuristic: Sort by area descending (largest first)
        items.sort(key=lambda x: (-x["area"], x["id"]))

        total_area = sum(i["area"] for i in items)
        if total_area > width * height:
            continue

        min_global_area = items[-1]["area"]  # Smallest item is last
        grid = [0] * height

        if solve_recursive(grid, items, 0, width, height, variations, min_global_area):
            valid_count += 1

    return valid_count


if __name__ == "__main__":
    print(part1(open("12.sample.txt" if environ.get("DEBUG") else "12.txt").read().splitlines()))
