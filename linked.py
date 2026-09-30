class Node:
    """리스트 소속과 양쪽 링크를 가진 노드."""
    def __init__(self, data, owner=None):
        self.data = data
        self.prev = None
        self.next = None
        self.owner = owner


class LinkedList:
    """센티넬 사이의 노드를 상수 시간에 연결하고 해제합니다."""
    def __init__(self):
        self.head = Node(None, self)
        self.tail = Node(None, self)
        self.head.next = self.tail
        self.tail.prev = self.head
        self.count = 0

    def _between(self, node, before, after):
        node.prev, node.next, node.owner = before, after, self
        before.next = after.prev = node
        self.count += 1
        return node

    def insert_front(self, data):
        return self._between(Node(data), self.head, self.head.next)

    def insert_back(self, data):
        return self._between(Node(data), self.tail.prev, self.tail)

    def remove_node(self, node):
        if node.owner is not self or node is self.head or node is self.tail:
            raise ValueError('Node does not belong to this list')
        node.prev.next, node.next.prev = node.next, node.prev
        node.prev = node.next = node.owner = None
        self.count -= 1
        return node.data

    def remove_front(self):
        return None if self.count == 0 else self.remove_node(self.head.next)

    def remove_back(self):
        return None if self.count == 0 else self.remove_node(self.tail.prev)

    def move_to_front(self, node):
        self.remove_node(node)
        self._between(node, self.head, self.head.next)

    def nodes(self):
        current = self.head.next
        while current is not self.tail:
            yield current
            current = current.next
