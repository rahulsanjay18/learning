# Eng: questions and answers

## 2026-10-16 · Eng 0003 coding round: "is my code wrong? check kept saying it ran too long"

**Short answer: the answers are right, but the search is far too slow. One line is in the wrong place.**

What I ran: your pasted code against the lesson's exact check, in CPython (the page runs Pyodide, which is slower).

| | 8×8×8, (0,0,0)→(7,7,7) | 9×9×9, (0,0,0)→(8,8,8) | full check (incl. 30×30×30) |
|---|---|---|---|
| your code | 7 ✓, **2,385,473** queue pushes, 6.2 s | 8 ✓, **17,934,638** pushes, 65 s | didn't finish in 60 s |
| fixed (one line moved) | 7 ✓ | 8 ✓ | **passes in 0.6 s** |

Your 24 vectors are all correct and distinct, and the 3×3×3 center correctly returns -1. So it wasn't an infinite loop.

### The bug: mark a cell explored when you push it, not when you pop it

You run `explored.add(coordinate)` after `popleft()`. Between a cell being queued and being popped, every other neighbour that
reaches it also sees "not explored" and queues it again. The same cell ends up in the queue many times, and each copy queues its
own neighbours again. The board has 512 cells, and the queue got 2.4 million pushes.

The fix: add a cell to `explored` at the moment you append it. Then each cell enters the queue at most once, so the cost is
O(24·n³) time and O(n³) space. This is the standard BFS from CLRS: a vertex is "discovered" the first time it is encountered,
and "the queue contains all the gray [discovered] vertices"; "every vertex reachable from s is discovered at most once"
(Cormen et al., *Introduction to Algorithms*, 4th ed., §20.2) [1].

```python
for v in list_vectors:
    c = (coordinate[0]+v[0], coordinate[1]+v[1], coordinate[2]+v[2])
    if c not in explored and all(0 <= x < n for x in c):
        explored.add(c)                 # mark on push
        queue.append((c, distance + 1))
```

(Your answers stayed correct because BFS still pops cells in order of distance. Only the duplicates made it slow.)

Interview takeaway: "where do I mark visited?" is the classic BFS slip. Saying "I mark on enqueue so each cell is queued once"
out loud is a good signal.

### Writing the 24 vectors compactly

Every knight move is some ordering of (0, 1, 2) with signs applied. `itertools.permutations` gives the 6 orderings and
`itertools.product` the sign choices [2]:

```python
from itertools import permutations, product

moves = {tuple(s * x for s, x in zip(signs, p))
         for p in permutations((0, 1, 2))
         for signs in product((1, -1), repeat=3)}   # a set: the sign on 0 makes duplicates
```

That's 6 × 8 = 48 combinations, which collapse to 24 because flipping the sign of the 0 does nothing. I checked that it gives the
same 24 vectors as your hand-written list. A filter version (the one the lesson's check uses) is also common:

```python
moves = [d for d in product(range(-2, 3), repeat=3) if sorted(map(abs, d)) == [0, 1, 2]]
```

In an interview the filter version is the easiest to defend: "a knight move is a vector whose absolute values are 0, 1, 2 in some
order". It's short to say and obviously correct.

### Sources
1. Cormen, Leiserson, Rivest, Stein, *Introduction to Algorithms*, 4th ed. (MIT Press, 2022), §20.2 "Breadth-first search" (in collection).
2. Python documentation, `itertools.permutations` and `itertools.product`: https://docs.python.org/3/library/itertools.html
