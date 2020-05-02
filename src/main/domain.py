from feed.settings import nanny_params
from flask.sessions import SessionMixin
import requests

class FeedHistory(dict, SessionMixin):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.data = kwargs.get('data', [kwargs.get('home')])
        self.increment = kwargs.get('increment')
        self.pagesProcessed = kwargs.get('pagesProcessed')

    def updatePagesProcessed(self):
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

    def get(self, ind):
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

    @property
    def home_config(self):
        hcReq = requests.get("http://{host}:{port}/parametercontroller/getParameter/router/{name}".format(**nanny_params, name=name))
        if hcReq.status_code == 404:
            return dict(page={'increment': 1}, skeleton=[], sort_first={'newest': '', 'oldest': '', 'high': '', 'low': ''})
        else:
            return hcReq.json()

    def small_dict(self):
        return dict(url=self.getLast(), increment=self.increment, pagesProcessed=self.pagesProcessed, name=self.name)

    def __dict__(self):
        return dict(increment=self.increment, pagesProcessed=self.pagesProcessed, data=self.data, name=self.name)

