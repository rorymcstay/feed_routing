import os

import requests
import time

from json.decoder import JSONDecodeError

from feed.logger import getLogger
from feed.settings import nanny_params
from flask import Response, request

logging = getLogger(__name__)

class List:
    def __init__(self, increment, home):
        self.data = []
        self.increment = increment
        self.pagesProcessed = 1
        self.data.append(home)

    def updatePagesProcessed(self):
        self.pagesProcessed += 1

    def add(self, item):
        self.data.append(item)

    def size(self):
        return len(self.data)

    def get(self, ind):
        if ind >= self.size():
            return self.data[-1]
        return self.data[ind]

    def clear(self):
        self.data = []

    def getLast(self):
        try:
            return self.data[-1]
        except IndexError as ex:
            return ''

    def __dict__(self):
        return dict(url=self.getLast(), increment=self.increment, pagesProcessed=self.pagesProcessed)

class History:
    lists = {}
    def __init__(self, manager):
        self.pagesProcessed = 0
        self.manager = manager

    @staticmethod
    def get_current_name(name):
        return "{}-history-{}".format(name, time.strftime("%d_%m"))

    def get_list(self, name):
        if self.lists.get(History.get_current_name(name)) is None:
            self.lists.update({name: List(increment=self.manager.home_config.get(name)['page']['increment'],
                                          home=self.manager.getResultPageUrl(name))})
        return self.lists.get(History.get_current_name(name))

    def add_history_object(self, name, **kwargs):
        logging.info(f'adding new history object {name} ')
        increment = kwargs.get('increment')
        home = kwargs.get('startUrl')
        self.lists.update({History.get_current_name(name): List(increment=increment, home=home)})

class RoutingManager(object):

    def __init__(self):
        self.hz = History(self)
        try:
            self.names = requests.get("http://{host}:{port}/parametercontroller/getFeeds/".format(**nanny_params)).json()
            logging.info(f'have feeds {self.names}')
        except JSONDecodeError as ex:
            logging.error(f'couldnt get feed names ')
            self.names = []
        self.home_config = {}
        for name in self.names:
            try:
                self.home_config.update({
                    name: requests.get(
                        "http://{host}:{port}/parametercontroller/getParameter/router/{name}".format(**nanny_params,
                                                                                                     name=name)
                    ).json()})
            except JSONDecodeError as ex:
                logging.warning(f'no routing params for {name}')
                continue
        logging.info(f'loaded parameters for: {self.names}')

    def initialiseChainHistory(self, name):
        actQ = requests.get("http://{host}:{port}/actionsmanager/queryActionChain/{name}/startUrl".format(name=name, **nanny_params))
        if actQ.status_code == 404:
            return Response('chain params not found')
        else:
            url = actQ.json().get('startUrl')
        self.hz.add_history_object(name, startUrl=url, increment=1)
        return 'ok'

    def getResultPageUrl(self, name, make=None, model=None, page=None, sort="newest"):
        if self.home_config.get(name) is None:
            logging.info(f'{name} is not currently being managed')
            return 'not found'
        if page is not None:
            page = self.home_config[name]["page"]["increment"] * page
        url = ""
        for substring in self.home_config[name]["skeleton"]:
            if "MAKE" in substring.upper() and make is None:
                continue
            if "MODEL" in substring.upper() and model is None:
                continue
            if "PAGE" in substring.upper() and page is None:
                page = 1
            url = url + substring
        if self.home_config[name].get("sort_first"):
            sort = self.home_config[name].get("sort_first")[sort]
        else:
            sort = None
        url = url.format(make=make, model=model, page=page, sort=sort)
        return url

    def updateHistory(self, name, value):
        if self.verifyItem(value, name):
            history: List = self.hz.get_list(name)
            history.add(value)
            history.updatePagesProcessed()
            logging.info("history updated for {}".format(History.get_current_name(name)))
            return "added one item to the cache"
        else:
            logging.warning("did not update history for name={}, url={}".format(name, value))
            return "no"

    def getLastPage(self, name):
        logging.info(f'getting last page for {name}')
        if self.hz.get_list(name) is None:
            self.initialiseChainHistory(name)
        history: List = self.hz.get_list(name)
        return history.__dict__()

    def clearHistory(self, name):
        history: List = self.hz.get_list(name)
        history.clear()

    def verifyItem(self, item, name):
        if self.home_config.get(name).get("skeleton")[0].strip('/') in str(item):
            return True
        else:
            return False
