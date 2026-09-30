from linked import LinkedList


class HashMap:
    """UTF-8 다항식 해시와 연결 리스트 체이닝을 사용합니다."""
    def __init__(self, capacity=8):
        self.capacity = max(2, capacity)
        self.buckets = [None] * self.capacity
        self.count = 0

    def _index(self, key):
        number = 0
        for byte in key.encode('utf-8'):
            number = (number * 131 + byte) & 0xffffffff
        return number % self.capacity

    def _find(self, key):
        bucket = self.buckets[self._index(key)]
        if bucket:
            for node in bucket.nodes():
                if node.data[0] == key:
                    return node
        return None

    def put(self, key, value):
        node = self._find(key)
        if node:
            node.data = (key, value)
            return
        index = self._index(key)
        if self.buckets[index] is None:
            self.buckets[index] = LinkedList()
        self.buckets[index].insert_back((key, value))
        self.count += 1
        if self.count / self.capacity > 0.75:
            old = self.buckets
            self.capacity *= 2
            self.buckets = [None] * self.capacity
            self.count = 0
            for bucket in old:
                if bucket:
                    for node in bucket.nodes():
                        self.put(node.data[0], node.data[1])

    def get(self, key):
        node = self._find(key)
        return node.data[1] if node else None

    def contains(self, key):
        return self._find(key) is not None

    def remove(self, key):
        node = self._find(key)
        if node is None:
            return None
        value = node.data[1]
        self.buckets[self._index(key)].remove_node(node)
        self.count -= 1
        return value

    def keys(self):
        for bucket in self.buckets:
            if bucket:
                for node in bucket.nodes():
                    yield node.data[0]

    def size(self):
        return self.count
