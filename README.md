# pycalltrak
Poor Man's Call Trace Analyzer&amp;Visualizer

It is a bit different than normal callgraph outputs. PyCalltrak will output every function call with different arguments. This means if a function is called multiple times with different arguments, then all of those calls will be visible in the callgraph as distinct nodes.

This project is a *toy project* and used specifically while developing/trying out/playing with different algorithms on various subjects. I used calltrak summary and visualizer(it still outputs ASCII, a GUI backend can be easily written) to find repetitive calls happening throughout the execution flow. An example is worth thousand words.

Following is a Travelling Salesman Problem Solver using Top-Down Dynamic Programming algorithm:
```python
import sys
from functools import lru_cache

A = [[11, 10, 15, 20, 3, 7, 16, 21], [10, 1, 35, 25, 3, 7, 16, 21],
     [15, 35, 1, 30, 3, 7, 16, 21], [20, 25, 30, 1, 3, 7, 16, 21],
     [20, 25, 30, 3, 7, 7, 16, 21], [20, 25, 30, 45, 3, 1, 16, 21],
     [20, 25, 30, 5, 3, 7, 3, 21], [20, 25, 30, 66, 3, 7, 16, 1]]
S = frozenset([x for x in range(len(A))]) # use frozenset to make Set hashable for lru_cache

#@lru_cache(maxsize=None)
def tsp(x, S):
    if not len(S):
        return A[x][0]
    r = sys.maxsize
    for y in S:
        r = min(r, A[x][y] + tsp(y, S - {y}))
    return r

import calltrak
calltrak.start()
r = tsp(0, S - {0})
calltrak.stop()
stats = calltrak.get_stats()
print(stats.summary())
#print(stats.to_json())
```
It will output following:

```
13700 call(s) in total. 13650(99%) recurring call(s).
```

Now if you enable lru_cache decorator which enables memoization on the function and re-run the example:
```
449 call(s) in total. 0(0%) recurring call(s).
```

Now, if you would like to visualize the call graph at this point, pycalltrak already have outlined the x,y coords needed to print out the stats. If you want to do it in your own way, then you need to traverse the callgraph and decide the topology of the graph yourself. A simple example using a single coordinate to print out a Left-Aligned call graph:

```python
for stat in stats:
    print((f'{"." * (stat.y-1)} {stat}'))
```

The output will be as following: (used different input than the example above)

```
16 call(s) in total. 6(37%) recurring call(s).
 tsp(x=0, S=frozenset({1, 2, 3})) -> 80 [0.00s]
. tsp(x=1, S=frozenset({2, 3})) -> 70 [0.00s]
. tsp(x=2, S=frozenset({1, 3})) -> 65 [0.00s]
. tsp(x=3, S=frozenset({1, 2})) -> 75 [0.00s]
.. tsp(x=2, S=frozenset({3})) -> 50 [0.00s]
.. tsp(x=3, S=frozenset({2})) -> 45 [0.00s]
.. tsp(x=1, S=frozenset({3})) -> 45 [0.00s]
.. tsp(x=3, S=frozenset({1})) -> 35 [0.00s]
.. tsp(x=1, S=frozenset({2})) -> 50 [0.00s]
.. tsp(x=2, S=frozenset({1})) -> 45 [0.00s]
... tsp(x=3, S=frozenset()) -> 20 [0.00s]
... tsp(x=2, S=frozenset()) -> 15 [0.00s]
... tsp(x=3, S=frozenset()) -> 20 [0.00s]
... tsp(x=1, S=frozenset()) -> 10 [0.00s]
... tsp(x=2, S=frozenset()) -> 15 [0.00s]
... tsp(x=1, S=frozenset()) -> 10 [0.00s]
```
