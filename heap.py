from storage import DynamicArray


class MinHeap:
    """가장 이른 만료 항목을 루트에 유지합니다."""
    def __init__(self):
        self.array = DynamicArray()

    def size(self):
        return self.array.length

    def peek(self):
        return self.array.get(0) if self.size() else None

    def _swap(self, a, b):
        value = self.array.get(a)
        self.array.set(a, self.array.get(b))
        self.array.set(b, value)

    def _heapify_up(self, index):
        while index:
            parent = (index - 1) // 2
            if self.array.get(parent) <= self.array.get(index):
                break
            self._swap(parent, index)
            index = parent

    def _heapify_down(self, index):
        while index * 2 + 1 < self.size():
            child = index * 2 + 1
            if child + 1 < self.size() and self.array.get(child + 1) < self.array.get(child):
                child += 1
            if self.array.get(index) <= self.array.get(child):
                break
            self._swap(index, child)
            index = child

    def push(self, value):
        self.array.append(value)
        self._heapify_up(self.size() - 1)

    def pop(self):
        if not self.size():
            return None
        first = self.array.get(0)
        last = self.array.remove(self.size() - 1)
        if self.size():
            self.array.set(0, last)
            self._heapify_down(0)
        return first
