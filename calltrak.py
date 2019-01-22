import sys
import time
import inspect
import traceback

_leaf_nodes = set()
_root = None
_frame_node_dict = {}
_unique_ncalls = 0


class Node(object):
    #__slots__ = ('val', 'parent', 'max_width', 'x', 'y', 'x_margin', 'children',
    #             '_t0', 'elapsed')

    def __init__(self, val, parent):
        self.val = val
        self.parent = parent
        self.max_width = 0
        self.x = 0
        self.x_margin = 0
        self.y = 0
        self._t0 = 0
        self.elapsed = 0
        self.children = []
        if parent:
            parent.children.append(self)

    def __repr__(self):
        s = self.val['call_formatted']
        if self.val['return_value']:
            s += '->%s' % (self.val['return_value'], )
        if self.val['exception_value']:
            s += '->exception=(%s)' % (self.val['exception_value'], )

        s += ' [%0.2fs]' % (self.elapsed)

        return s


def _FFC(frame):
    a_v = inspect.getargvalues(frame)
    return frame.f_code.co_name + inspect.formatargvalues(*a_v)


def _trace_calls(frame, event, arg):
    global _root

    def _get_parent(f):
        for cf, _ in traceback.walk_stack(f):
            if cf in _frame_node_dict:
                return _frame_node_dict[cf]

    if frame.f_code.co_name == 'stop':
        return

    if event not in ['call', 'return', 'exception']:
        return

    # a frame object is a stack frame and thus: is unique to each invocation of a
    # function
    if event == 'call':
        d = {
            'call_formatted': _FFC(frame),
            'return_value': None,
            'exception_value': None
        }
        parent_node = _get_parent(frame)
        cur_node = Node(d, parent_node)
        if not parent_node:
            _root = cur_node
        _frame_node_dict[frame] = cur_node
        cur_node._t0 = time.time()

        # maintain leaf nodes
        if parent_node in _leaf_nodes:
            _leaf_nodes.remove(parent_node)
        _leaf_nodes.add(cur_node)
    else:
        # maybe a function is started being traced in the middle of execution
        #if hasattr(frame, '_calltrak_node'):
        if frame in _frame_node_dict:
            cur_node = _frame_node_dict[frame]
            cur_node.val['%s_value' % (event)] = arg
            cur_node.elapsed = time.time() - cur_node._t0

    if event == 'call':
        return _trace_calls


def start():
    sys.settrace(_trace_calls)


def stop():
    sys.settrace(None)


def _stats_pre_processing():
    '''
    Calculates the max_width, coords, unique call count...etc,
    generally the stuff that is needed to render a valid callgraph with ease.
    '''
    global _unique_ncalls

    def _get_x_margin(node):
        if len(node.children) in [1, 2]:
            return 0
        middle_pos = (node.max_width) // 2
        c_pos = 0
        min_dist = node.max_width

        for child in node.children:
            c_pos += child.max_width
            dist = abs(middle_pos - c_pos)
            if dist > min_dist:
                return c_pos - child.max_width
            if dist < min_dist:
                min_dist = dist
                continue
            else:
                break

        return c_pos

    # walk from leaf to root and update max_width, this is basically a reverse
    # level order traversal
    q = list(_leaf_nodes)
    while q:
        node = q.pop()
        if node.parent:
            node.parent.max_width += 1
            q.insert(0, node.parent)
        if not node.children:
            node.max_width = 1

    # do level order traversal and set coordinates
    unique_calls = set()
    q = [_root]
    _root.x = 1    # TODO: Change below to 0 after dealing bound checks in app. code
    _root.y = 1
    _root.x_margin = _get_x_margin(_root)
    while q:
        node = q.pop()

        # do unique call calculation
        if node.val['call_formatted'] in unique_calls:
            unique_calls.remove(node.val['call_formatted'])
        else:
            unique_calls.add(node.val['call_formatted'])

        # TODO: Maybe hold a heap instead of this
        #node.children = sorted(node.children, key=attrgetter('max_width'))

        c_x = node.x
        for child in node.children:
            child.x_margin = _get_x_margin(child)
            child.x = c_x
            child.y = node.y + 1
            c_x += child.max_width

            q.insert(0, child)

    _unique_ncalls = len(unique_calls)


def get_summary():
    _stats_pre_processing()

    return f"{len(_frame_node_dict)} call(s) in total. " \
        f"{100 * (len(_frame_node_dict) - _unique_ncalls) // len(_frame_node_dict)}% " \
        f"of them are recurring calls."


def get_stats():
    _stats_pre_processing()

    # do a level order traversal on stats
    stats_q = [_root]
    while stats_q:
        node = stats_q.pop()
        yield node
        for child in node.children:
            stats_q.insert(0, child)
