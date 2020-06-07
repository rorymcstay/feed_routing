from feed.settings import nanny_params
from flask.sessions import SessionMixin
import requests

class FeedHistory(dict, SessionMixin):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.data = kwargs.get('data', [kwargs.get('home')])
        self.increment = kwargs.get('increment')
        self.pagesProcessed = kwargs.get('pagesProcessed', 0)
        self.userID = kwargs.get('userID', None)

    def updatePagesProcessed(self):
        if self.pagesProcessed is None:
            self.pagesProcessed = 0
        self.pagesProcessed += 1
        self.modified = True

    def initialise(self, name, home):
        if len(self.data) > 1:
            pass
        else:
            self.data = [home]
        self.name = name
        self.modified = True

    def setName(self, name):
        self.name = name
        self.modified = True

    def add(self, item):
        self.data.append(item)
        self.modified = True

    def size(self):
        return len(self.data)

    def getHistoryItem(self, ind):
        if ind >= self.size():
            return self.data[-1]
        return self.data[ind]

    def clear(self):
        self.data = []
        self.modified = True

    def getLast(self):
        try:
            return self.data[-1]
        except IndexError as ex:
            return ''

    def small_dict(self):
        return dict(url=self.getLast(), increment=self.increment, pagesProcessed=self.pagesProcessed, name=self.name, userID=self.userID)

    def __dict__(self):
        return dict(increment=self.increment, pagesProcessed=self.pagesProcessed, data=self.data, name=self.name, userID=self.userID)

