class DynamicArray:
    """고정 크기 저장 배열을 두 배씩 늘립니다."""
    def __init__(self, capacity=8):
        self.capacity = max(1, capacity)
        self.storage = [None] * self.capacity
        self.length = 0

    def append(self, value):
        if self.length == self.capacity:
            grown = [None] * (self.capacity * 2)
            for i in range(self.length):
                grown[i] = self.storage[i]
            self.storage = grown
            self.capacity *= 2
        self.storage[self.length] = value
        self.length += 1

    def get(self, index):
        if not 0 <= index < self.length:
            raise IndexError(index)
        return self.storage[index]

    def set(self, index, value):
        if not 0 <= index < self.length:
            raise IndexError(index)
        self.storage[index] = value

    def remove(self, index):
        value = self.get(index)
        for i in range(index, self.length - 1):
            self.storage[i] = self.storage[i + 1]
        self.length -= 1
        self.storage[self.length] = None
        return value
