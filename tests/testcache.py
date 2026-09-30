import random
import unittest
from cache import Cache
from hashmap import HashMap
from heap import MinHeap
from linked import LinkedList
from storage import DynamicArray


class StructuresTests(unittest.TestCase):
    def test_list_singleton_and_move(self):
        linked = LinkedList()
        first = linked.insert_front('a')
        second = linked.insert_back('b')
        linked.move_to_front(second)
        self.assertEqual(linked.remove_front(), 'b')
        self.assertEqual(linked.remove_back(), 'a')
        self.assertIsNone(linked.remove_front())
        with self.assertRaises(ValueError):
            linked.remove_node(first)

    def test_hash_collision_resize_and_none(self):
        mapping = HashMap()
        for key in ['a', 'i', 'q']:
            mapping.put(key, key.upper())
        mapping.put('i', 'changed')
        self.assertEqual(mapping.get('i'), 'changed')
        self.assertEqual(mapping.remove('a'), 'A')
        self.assertEqual(mapping.get('q'), 'Q')
        for i in range(1000):
            mapping.put(str(i), i)
        for i in range(1000):
            self.assertEqual(mapping.get(str(i)), i)
        mapping.put('none', None)
        self.assertTrue(mapping.contains('none'))
        self.assertEqual(mapping.size(), 1003)
        self.assertGreaterEqual(mapping.capacity, 2048)

    def test_heap_and_dynamic_capacity(self):
        randomizer = random.Random(42)
        values = [randomizer.randrange(10000) for _ in range(500)]
        heap = MinHeap()
        for value in values:
            heap.push((value, 'key'))
        previous = -1
        for _ in values:
            value, key = heap.pop()
            self.assertGreaterEqual(value, previous)
            previous = value
        self.assertIsNone(heap.pop())
        array = DynamicArray(1)
        array.append('a')
        array.append('b')
        array.set(0, 'c')
        self.assertEqual(array.capacity, 2)
        self.assertEqual(array.remove(0), 'c')
        self.assertEqual(array.get(0), 'b')


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.now = 0.0
        self.cache = Cache(lambda: self.now)

    def command(self, text):
        return self.cache.execute(text)

    def test_lru_touch_eviction_and_oom_preserve_existing(self):
        self.command('CONFIG SET maxmemory 6')
        self.command('SET a aa')
        self.command('SET b bb')
        self.command('GET a')
        self.command('SET c cc')
        self.assertEqual(self.command('GET b'), '(nil)')
        self.assertEqual(self.cache.evicted_keys, 1)
        self.assertIn('OOM', self.command('SET a toolong'))
        self.assertEqual(self.command('GET a'), '"aa"')
        self.assertEqual(self.cache.used_memory, 6)

    def test_ttl_overwrite_del_reuse_and_reschedule(self):
        self.command('SET a x')
        self.command('EXPIRE a 3')
        self.command('SET a y')
        self.now = 4
        self.assertEqual(self.command('GET a'), '"y"')
        self.assertEqual(self.command('TTL a'), '(integer) -1')
        self.command('EXPIRE a 10')
        self.command('EXPIRE a 20')
        self.now = 15
        self.assertEqual(self.command('GET a'), '"y"')
        self.command('DEL a')
        self.command('SET a z')
        self.command('EXPIRE a 30')
        self.now = 25
        self.assertEqual(self.command('GET a'), '"z"')
        self.now = 46
        self.assertEqual(self.command('TTL a'), '(integer) -2')
        self.assertEqual(self.cache.used_memory, 0)
        self.assertEqual(self.cache.lru.count, 0)

    def test_expiration_before_dbsize_and_keys(self):
        self.command('SET a x')
        self.command('EXPIRE a 1')
        self.now = 1
        self.assertEqual(self.command('DBSIZE'), '(integer) 0')
        self.assertEqual(self.command('KEYS'), '(empty array)')
        self.assertEqual(self.command('EXPIRE absent 3'), '(integer) 0')

    def test_unicode_bytes_quotes_and_invalid_commands(self):
        self.command('SET 이름 "신 예준"')
        self.assertEqual(self.cache.used_memory, len('이름신 예준'.encode('utf-8')))
        self.assertEqual(self.command('GET 이름'), '"신 예준"')
        for invalid in ['HELLO', 'GET', 'CONFIG SET maxmemory abc', 'CONFIG SET maxmemory -1', 'SET "unclosed']:
            self.assertTrue(self.command(invalid).startswith('(error)'))
        self.assertEqual(self.command('EXPIRE 이름 0'), '(integer) 1')
        self.assertEqual(self.command('DEL 이름'), '(integer) 0')


if __name__ == '__main__':
    unittest.main()
