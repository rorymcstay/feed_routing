import os

import requests
import time

from hazelcast import HazelcastClient, ClientConfig
from hazelcast.proxy import List

from feed.logger import logger as logging
from feed.settings import hazelcast_params, nanny_params


class RoutingManager(object):
    config = ClientConfig()
    config.network_config.addresses.append("{host}:{port}".format(**hazelcast_params))
    hz = HazelcastClient(config)

    def __init__(self):
        self.names = requests.get("http://{host}:{port}/parametercontroller/getFeeds/".format(**nanny_params)).json()
        self.home_config = {}
        for name in self.names:
            self.home_config.update({
                name: requests.get(
                    "http://{host}:{port}/parametercontroller/getParameter/router/{name}".format(**nanny_params,
                                                                                                 name=name)
                ).json()})

        logging.info("loaded parameters for: "+str(self.names))

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
            return "no"

    def getLastPage(self, name):
        histName = "{}-history-{}".format(name, time.strftime("%d_%m"))
        history: List = self.hz.get_list(histName)
        num = history.size().result()
        if num < 1:
            return False
        size = history.size().result()
        last = history.get(size - 1).result()
        url = str(last, "utf-8")
        payload = {"url": url,
                   "increment": self.home_config.get(name).get("page").get("increment")}
        return payload

    def clearHistory(self, name):
        histName = "{}-history-{}".format(name, time.strftime("%d_%m"))
        history: List = self.hz.get_list(histName)
        history.clear()

    def verifyItem(self, item, name):
        if self.home_config.get(name).get("skeleton")[0] in str(item):
            return True
        else:
            return False
