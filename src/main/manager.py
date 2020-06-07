import os

import requests

from json.decoder import JSONDecodeError

from feed.logger import getLogger
from feed.settings import nanny_params
from flask import Response, request, session, jsonify
from flask_classy import FlaskView, route

logging = getLogger(__name__)


class RoutingController(FlaskView):

    def initialiseRoutingSession(self, name):
        if session.name is None:
            # do not give default, as there should be validation on actionChain insertion.
            # No point sending crawler somewhere constant. if we blow up here it is fine - we will here about it.
            startUrl = session["nanny"].get(f'/actionsmanager/queryActionChain/{name}/startUrl', resp=True).get('startUrl')
            session.initialise(home=startUrl, name=name)
        return Response('ok')

    def updateHistory(self, name):
        value = str(request.data, 'utf-8')
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

    @route('clearHistory/<string:name>', methods=['DELETE', 'GET'])
    def clearHistory(self, name):
        session.clear()
        return Response('ok', status=200)

    def _verifyItem(self, item, name):
        return True

