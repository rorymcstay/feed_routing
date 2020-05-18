import logging
import os

from feed.settings import nanny_params
from flask import Flask

from src.main.manager import RoutingController
from src.main.domain import FeedHistory
from feed.service import Service, Client
from feed.chainsessions import init_app

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logging.FileHandler('/var/tmp/myapp.log')

nanny = Client("nanny", **nanny_params)



app = init_app(FeedHistory)

RoutingController.register(app)
Service.register(app)


if __name__ == '__main__':
    logging.info("\n".join([f'{key}={os.environ[key]}' for key in os.environ]))
    print(app.url_map)
    app.run(port=os.getenv("FLASK_PORT", os.getenv("ROUTING_PORT", 5003)), host=os.getenv('ROUTER_HOST'))

