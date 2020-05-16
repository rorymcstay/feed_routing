import os

import requests

from json.decoder import JSONDecodeError

from feed.logger import getLogger
from feed.settings import nanny_params
from flask import Response, request, session, jsonify
from flask_classy import FlaskView, route

logging = getLogger(__name__)


class RoutingController(FlaskView):

    def getResultPageUrl(self, name):

        options = request.json
        if options is None:
            options = {}
        if page is not None:
            page = session.home_config.get("page").get("increment") * page
        url = ""
        model, make, page, sort = option.get('model'), option.ger('make'), option.get('page'), option.get('sort', 'newest')

        for substring in session.home_config.get("skeleton"):
            if "MAKE" in substring.upper() and make is None:
                continue
            if "MODEL" in substring.upper() and model is None:
                continue
            if "PAGE" in substring.upper() and page is None:
                page = 1
            url = url + substring

        if session.home_config.get("sort_first"):
            sort = session.home_config[name].get("sort_first")[sort]
        else:
            sort = None
        url = url.format(make=make, model=model, page=page, sort=sort)
        if url == '':
            logging.error(f'url returned empty, returning home url')
            return session.getLast()
        return url

    def initialiseRoutingSession(self, name):
        if session.name is None:
            startUrl = requests.get('http://{host}:{port}/actionsmanager/queryActionChain/{name}/startUrl'.format(name=name, **nanny_params)).json().get('startUrl')
            session.initialise(home=startUrl, name=name)
        return Response('ok')

    def updateHistory(self, name):
        value = str(request.data)
        if self._verifyItem(value, name):
            session.add(value)
            session.updatePagesProcessed()
            logging.info("history updated for {}".format(session.get('session_id')))
            return Response('ok', status=200)
        else:
            logging.warning("History verification check returned false: name=[{}], url=[{}]".format(name, value))
            return Response('ok', status=400)

    def getLastPage(self, name):
        lastPage = session.small_dict()
        if session.name:
            resp = jsonify(lastPage) # type: Response
            resp.status_code = 200
            resp.mimetype = 'application/json'
            return resp
        else:
            resp = jsonify({'url': None})
            resp.status_code = 404
            resp.mimetype = 'application/json'
            return resp

    @route('clearHistory/<string:name>', methods=['DELETE'])
    def clearHistory(self, name):
        session.clear()
        return Response('ok', status=200)

    def _verifyItem(self, item, name):
        if not session.home_config or session.home_config.get("skeleton")[0].strip('/') in str(item):
            return True
        else:
            return False

