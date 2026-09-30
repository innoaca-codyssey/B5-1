import math
import shlex
import time
from hashmap import HashMap
from linked import LinkedList
from heap import MinHeap


class Entry:
    """키의 값, 만료 세대와 LRU 노드를 연결합니다."""
    def __init__(self, key, value):
        self.key, self.value = key, value
        self.expires = None
        self.generation = 0
        self.node = None

    def bytes(self):
        return len(self.key.encode('utf-8')) + len(self.value.encode('utf-8'))


class Cache:
    """해시 조회, LRU 이동과 힙 만료 처리를 조합한 저장소."""
    def __init__(self, clock=time.monotonic):
        self.data = HashMap()
        self.lru = LinkedList()
        self.expiry = MinHeap()
        self.clock = clock
        self.maxmemory = self.used_memory = self.evicted_keys = 0
        self.generation = 0

    def _delete(self, key):
        entry = self.data.remove(key)
        if entry is None:
            return 0
        self.lru.remove_node(entry.node)
        self.used_memory -= entry.bytes()
        entry.expires = None
        return 1

    def _expire(self):
        now = self.clock()
        while self.expiry.size() and self.expiry.peek()[0] <= now:
            deadline, generation, key = self.expiry.pop()
            entry = self.data.get(key)
            if entry and entry.generation == generation and entry.expires == deadline:
                self._delete(key)

    def _evict(self):
        while self.maxmemory and self.used_memory > self.maxmemory:
            self._delete(self.lru.tail.prev.data.key)
            self.evicted_keys += 1

    def execute(self, command):
        try:
            args = shlex.split(command)
        except ValueError:
            return '(error) ERR invalid quotes'
        if not args:
            return ''
        cmd = args[0].upper()
        self._expire()
        expected = None
        if cmd == 'SET':
            expected = 3
        elif cmd in ('GET', 'DEL', 'EXISTS', 'TTL'):
            expected = 2
        elif cmd in ('DBSIZE', 'KEYS'):
            expected = 1
        elif cmd == 'EXPIRE':
            expected = 3
        elif cmd == 'CONFIG':
            expected = 4
        elif cmd == 'INFO':
            expected = 2
        if expected is None:
            return "(error) ERR unknown command '" + args[0] + "'"
        if len(args) != expected:
            return "(error) ERR wrong number of arguments for '" + cmd + "' command"
        if cmd == 'CONFIG' and (args[1].upper() != 'SET' or args[2].lower() != 'maxmemory') or cmd == 'INFO' and args[1].lower() != 'memory':
            return '(error) ERR invalid subcommand'
        if cmd in ('CONFIG', 'EXPIRE'):
            try:
                integer = int(args[-1])
                if cmd == 'CONFIG' and integer < 0 or abs(integer) > 2**63 - 1:
                    raise ValueError
            except ValueError:
                return '(error) ERR value is not an integer or out of range'
        if cmd == 'SET':
            new = Entry(args[1], args[2])
            if self.maxmemory and new.bytes() > self.maxmemory:
                return "(error) OOM command not allowed when used_memory > 'maxmemory'"
            self._delete(new.key)
            new.node = self.lru.insert_front(new)
            self.data.put(new.key, new)
            self.used_memory += new.bytes()
            self._evict()
            return 'OK'
        if cmd == 'CONFIG':
            self.maxmemory = integer
            self._evict()
            return 'OK'
        if cmd == 'INFO':
            return f'used_memory:{self.used_memory}\nmaxmemory:{self.maxmemory}\nevicted_keys:{self.evicted_keys}'
        if cmd == 'DBSIZE':
            return f'(integer) {self.data.size()}'
        if cmd == 'KEYS':
            output = ''
            for index, key in enumerate(self.data.keys(), 1):
                output += f'{index}. "{key}"\n'
            return output.rstrip() or '(empty array)'
        entry = self.data.get(args[1])
        if cmd == 'GET':
            if entry is None:
                return '(nil)'
            self.lru.move_to_front(entry.node)
            return '"' + entry.value + '"'
        if cmd == 'DEL':
            return f'(integer) {self._delete(args[1])}'
        if cmd == 'EXISTS':
            return f'(integer) {int(entry is not None)}'
        if cmd == 'TTL':
            if entry is None:
                return '(integer) -2'
            if entry.expires is None:
                return '(integer) -1'
            return f'(integer) {max(0, math.floor(entry.expires - self.clock()))}'
        if cmd == 'EXPIRE':
            if entry is None:
                return '(integer) 0'
            if integer <= 0:
                return f'(integer) {self._delete(args[1])}'
            self.generation += 1
            entry.generation = self.generation
            entry.expires = self.clock() + integer
            self.expiry.push((entry.expires, entry.generation, entry.key))
            return '(integer) 1'
