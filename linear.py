from linked import LinkedList

class Stack:
    """앞쪽에서 넣고 빼는 LIFO 저장소."""
    def __init__(self):
        self.items=LinkedList()
    def push(self,value):
        self.items.insert_front(value)
    def pop(self):
        return self.items.remove_front()
    def size(self):
        return self.items.count

class Queue:
    """뒤에 넣고 앞에서 빼는 FIFO 저장소."""
    def __init__(self):
        self.items=LinkedList()
    def enqueue(self,value):
        self.items.insert_back(value)
    def dequeue(self):
        return self.items.remove_front()
    def size(self):
        return self.items.count

class Deque:
    """양쪽 끝에서 상수 시간에 삽입/삭제합니다."""
    def __init__(self):
        self.items=LinkedList()
    def push_left(self,value):
        self.items.insert_front(value)
    def push_right(self,value):
        self.items.insert_back(value)
    def pop_left(self):
        return self.items.remove_front()
    def pop_right(self):
        return self.items.remove_back()
