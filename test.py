#
#print(_root.val, _root.max_width)
import calltrak
import curses
from curses import wrapper


def main(stdscr):
    stdscr.resize(5000, 5000)
    stdscr.clear()

    NODE_WIDTH = 25

    for node in calltrak.get_stats():
        stdscr.addstr(node.y * 3, (node.x + node.x_margin) * NODE_WIDTH,
                      str(node)[:NODE_WIDTH])
        stdscr.addch((node.y * 3) - 1, (node.x + node.x_margin) * NODE_WIDTH,
                     '|')

        # hor. line starts where last child's text starts
        horizontal_line_length = 0
        debug = ''
        if len(node.children) > 1:
            #debug = (node.x_start, node.x_pos, node.max_width)
            horizontal_line_length = (node.children[-1].x + node.children[-1]
                                      .x_margin - node.x) * NODE_WIDTH
            stdscr.addstr((node.y * 3) + 1, (node.x) * NODE_WIDTH,
                          '_' * (horizontal_line_length) + (str(debug)))
        if len(node.children) >= 1:
            stdscr.addch((node.y * 3) + 1,
                         (node.x + node.x_margin) * NODE_WIDTH, '|')

    stdscr.refresh()
    stdscr.getkey()


from functools import lru_cache
import time


@lru_cache()
def fib(n):
    if n <= 1:
        return n

    time.sleep(0.3)

    r = fib(n - 1) + fib(n - 2)
    return r


calltrak.start()
#a(4)
fib(10)

#cc([1, 2, 5], 5)
calltrak.stop()

for node in calltrak.get_stats():
    #print(node, node.max_width)
    #import jsonpickle
    import json
    #d = json.dumps(json.loads(jsonpickle.encode(node)), indent=4)
    #print(d)
    c = json.dumps(node, default=lambda o: o.__dict__)
    print(c)
    break

#wrapper(main)
#summary = calltrak.get_summary()
#print(summary)
