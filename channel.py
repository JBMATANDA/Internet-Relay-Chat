class ChannelQueue:
    def __init__(self):
        self.queue = []

    def enqueue(self,element):
        self.queue.insert(0,element)

    def dequeue(self,element):
        return self.queue.pop()


class Channel:
    def __init__(self, owner, channelname):
        self.owner = owner
        self.channelName = channelname
        self.userQueue = ChannelQueue()

    def addUser(self, user):
        self.userQueue.enqueue(user)

    def deleteUser(self,user):
        self.userQueue.dequeue(user)

    def changeOwner(self,user):
        pass

    def userExists(self,user):
        user_in_channel = False
        for i in self.userQueue.queue:
            if i == user:
                user_in_channel = True
        return user_in_channel

