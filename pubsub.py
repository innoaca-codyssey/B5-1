from hashmap import HashMap
from linear import Queue

class PubSub:
    """채널별 구독자와 구독자별 연결 리스트 FIFO를 관리합니다."""
    def __init__(self):
        self.channels=HashMap()
    def subscribe(self,channel,subscriber):
        members=self.channels.get(channel)
        if members is None:
            members=HashMap();self.channels.put(channel,members)
        if not members.contains(subscriber):members.put(subscriber,Queue())
    def unsubscribe(self,channel,subscriber):
        members=self.channels.get(channel)
        if members is not None:
            members.remove(subscriber)
            if members.size()==0:self.channels.remove(channel)
    def subscriptions(self,subscriber):
        return sum(1 for c in self.channels.keys() if self.channels.get(c).contains(subscriber))
    def publish(self,channel,message):
        members=self.channels.get(channel)
        if members is None:return 0
        for subscriber in members.keys():members.get(subscriber).enqueue(message)
        return members.size()
    def drain(self,subscriber):
        for channel in self.channels.keys():
            queue=self.channels.get(channel).get(subscriber)
            if queue is not None:
                while queue.size():yield channel,queue.dequeue()
