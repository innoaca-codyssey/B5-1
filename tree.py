from linear import Queue, Stack

class TreeNode:
    def __init__(self,data,left=None,right=None):
        self.data,self.left,self.right=data,left,right

class BinaryTree:
    """스택과 큐를 사용해 재귀 깊이 제한 없이 순회합니다."""
    def __init__(self,root=None):
        self.root=root
    def preorder(self):
        stack=Stack()
        if self.root:stack.push(self.root)
        while stack.size():
            node=stack.pop()
            yield node.data
            if node.right:stack.push(node.right)
            if node.left:stack.push(node.left)
    def inorder(self):
        stack,node=Stack(),self.root
        while node or stack.size():
            while node:
                stack.push(node);node=node.left
            node=stack.pop()
            yield node.data
            node=node.right
    def postorder(self):
        todo,done=Stack(),Stack()
        if self.root:todo.push(self.root)
        while todo.size():
            node=todo.pop();done.push(node)
            if node.left:todo.push(node.left)
            if node.right:todo.push(node.right)
        while done.size():yield done.pop().data
    def levelorder(self):
        queue=Queue()
        if self.root:queue.enqueue(self.root)
        while queue.size():
            node=queue.dequeue()
            yield node.data
            if node.left:queue.enqueue(node.left)
            if node.right:queue.enqueue(node.right)

class BST(BinaryTree):
    """작은 값은 왼쪽, 큰 값은 오른쪽에 두며 중복은 추가하지 않습니다."""
    def insert(self,value):
        if self.root is None:
            self.root=TreeNode(value);return True
        node=self.root
        while True:
            if value==node.data:return False
            direction='left' if value<node.data else 'right'
            child=getattr(node,direction)
            if child is None:
                setattr(node,direction,TreeNode(value));return True
            node=child
    def search(self,value):
        node=self.root
        while node and node.data!=value:
            node=node.left if value<node.data else node.right
        return node
    def delete(self,value):
        parent,node=None,self.root
        while node and node.data!=value:
            parent,node=node,node.left if value<node.data else node.right
        if node is None:return False
        if node.left and node.right:
            successor_parent,successor=node,node.right
            while successor.left:
                successor_parent,successor=successor,successor.left
            node.data=successor.data
            parent,node=successor_parent,successor
        child=node.left or node.right
        if parent is None:self.root=child
        elif parent.left is node:parent.left=child
        else:parent.right=child
        return True
