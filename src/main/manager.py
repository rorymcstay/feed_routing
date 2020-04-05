import os

import requests
import time

from json.decoder import JSONDecodeError

from feed.logger import getLogger 
from feed.settings import nanny_params

logging = getLogger(__name__)

class List:
    def __init__(self):
        self.data = []

    def add(self, item):
        self.data.append(item)
    def size(self):
        return len(self.data)
    def get(self, ind):
        if ind >= self.size():
            return self.data[-1]
        return self.data[ind]
    def clear():
        self.data = []

class History():
    lists = {}
    def get_list(self, name):
        if self.lists.get(name) is None:
            self.lists.update({name: List()})
        return self.lists.get(name)

class RoutingManager(object):
    hz = History()

    def __init__(self):
        try:
            self.names = requests.get("http://{host}:{port}/parametercontroller/getFeeds/".format(**nanny_params)).json()
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

    def getResultPageUrl(self, name, make=None, model=None, page=None, sort="newest"):
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
            histName = "{}-history-{}".format(name, time.strftime("%d_%m"))
            history: List = self.hz.get_list(histName)
            history.add(value)
            logging.info("history updated for {}".format(histName))

            return "added one item to the cache"

        else:
            logging.warning("did not update history for name={}, url={}".format(name, value))
            return "no"

    def getLastPage(self, name):
        histName = "{}-history-{}".format(name, time.strftime("%d_%m"))
        history: List = self.hz.get_list(histName)
        num = history.size()
        if num < 1:
            return False
        size = history.size()
        last = history.get(size - 1)
        url = str(last, "utf-8")
        payload = {"url": url,
                   "increment": self.home_config.get(name).get("page").get("increment")}
        return payload

    def clearHistory(self, name):
        histName = "{}-history-{}".format(name, time.strftime("%d_%m"))
        history: List = self.hz.get_list(histName)
        history.clear()

    def verifyItem(self, item, name):
        if self.home_config.get(name).get("skeleton")[0].strip('/') in str(item):
            return True
        else:
            return False
