from __future__ import annotations
import sys

def best_two_digits(s: str) -> int:
    # Choose i<j to maximize 10*s[i] + s[j]
    digits = [ord(c) - 48 for c in s.strip()]
    n = len(digits)
    if n < 2:
        return 0

    # suffix max digit
    sufmax = [0] * (n + 1)
    sufmax[n] = -1
    for i in range(n - 1, -1, -1):
        sufmax[i] = max(sufmax[i + 1], digits[i])

    best = -1
    for tens in range(9, 0, -1):
        # earliest position of 'tens' that has a later digit
        for i in range(n - 1):
            if digits[i] == tens:
                ones = sufmax[i + 1]
                if ones >= 0:
                    val = 10 * tens + ones
                    if val > best:
                        best = val
                break
        if best >= 0:
            break
    return best if best >= 0 else 0

def best_k_digits(s: str, k: int) -> int:
    # Greedy monotonic stack: maximum lexicographic subsequence length k
    digits = [c for c in s.strip()]
    n = len(digits)
    if k <= 0:
        return 0
    if n <= k:
        return int("".join(digits))

    remove = n - k
    st: list[str] = []
    for ch in digits:
        while remove > 0 and st and st[-1] < ch:
            st.pop()
            remove -= 1
        st.append(ch)
    if remove > 0:
        st = st[:-remove]
    st = st[:k]
    return int("".join(st))

def main() -> None:
    lines = [ln.strip() for ln in sys.stdin.read().splitlines() if ln.strip()]
    total1 = 0
    total2 = 0
    for ln in lines:
        total1 += best_two_digits(ln)
        total2 += best_k_digits(ln, 12)
    print(total1)
    print(total2)

if __name__ == "__main__":
    main()
