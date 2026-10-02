import unittest
from cache import Cache
from linear import Stack, Queue, Deque
from pubsub import PubSub
from tree import TreeNode, BinaryTree, BST


class BonusTests(unittest.TestCase):
    def test_stack_queue_deque_empty_and_order(self):
        stack,queue,deque=Stack(),Queue(),Deque()
        for value in [1,2,3]:
            stack.push(value);queue.enqueue(value)
        self.assertEqual([stack.pop(),stack.pop(),stack.pop()],[3,2,1])
        self.assertEqual([queue.dequeue(),queue.dequeue(),queue.dequeue()],[1,2,3])
        self.assertIsNone(queue.dequeue())
        deque.push_left(2);deque.push_left(1);deque.push_right(3)
        self.assertEqual([deque.pop_left(),deque.pop_right(),deque.pop_left()],[1,3,2])

    def test_binary_tree_four_traversals(self):
        tree=BinaryTree(TreeNode('A',TreeNode('B',TreeNode('D'),TreeNode('E')),TreeNode('C')))
        self.assertEqual(list(tree.preorder()),list('ABDEC'))
        self.assertEqual(list(tree.inorder()),list('DBEAC'))
        self.assertEqual(list(tree.postorder()),list('DEBCA'))
        self.assertEqual(list(tree.levelorder()),list('ABCDE'))
        self.assertEqual(list(BinaryTree().postorder()),[])

    def test_bst_leaf_single_child_two_children_and_root(self):
        tree=BST()
        for value in [5,3,7,2,4,6,8]:tree.insert(value)
        self.assertFalse(tree.insert(5))
        self.assertEqual(tree.search(6).data,6)
        for value in [2,3,5,7,4,6,8]:
            self.assertTrue(tree.delete(value))
            self.assertIsNone(tree.search(value))
            result=list(tree.inorder())
            self.assertTrue(all(a<b for a,b in zip(result,result[1:])))
        self.assertIsNone(tree.root)
        self.assertFalse(tree.delete(9))

    def test_bst_skew_no_recursion_failure(self):
        tree=BST()
        for i in range(1500):tree.insert(i)
        self.assertEqual(len(list(tree.inorder())),1500)
        self.assertTrue(tree.delete(1499))

    def test_pubsub_fanout_fifo_duplicates_and_unsubscribe(self):
        pubsub=PubSub()
        for user in ['a','b']:pubsub.subscribe('news',user)
        pubsub.subscribe('news','a')
        self.assertEqual(pubsub.publish('news','first'),2)
        self.assertEqual(pubsub.publish('news','second'),2)
        self.assertEqual(list(pubsub.drain('a')),[('news','first'),('news','second')])
        self.assertEqual(list(pubsub.drain('b')),[('news','first'),('news','second')])
        pubsub.unsubscribe('news','a')
        self.assertEqual(pubsub.publish('news','third'),1)
        self.assertEqual(list(pubsub.drain('a')),[])
        pubsub.unsubscribe('news','b')
        self.assertEqual(pubsub.channels.size(),0)

    def test_pubsub_cli_separate_from_key_memory(self):
        cache=Cache()
        self.assertEqual(cache.execute('PUBLISH news hi'),'(integer) 0')
        cache.execute('SUBSCRIBE news')
        self.assertEqual(cache.execute('PUBLISH news hi'),'(integer) 1')
        self.assertEqual(list(cache.pubsub.drain('cli')),[('news','hi')])
        self.assertEqual(cache.execute('DBSIZE'),'(integer) 0')
        self.assertEqual(cache.used_memory,0)


if __name__=='__main__':unittest.main()
