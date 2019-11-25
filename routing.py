import logging
import os

from feed.settings import nanny_params
from flask import Flask

from src.main.rest import RoutingController
from feed.service import Service, Client

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logging.FileHandler('/var/tmp/myapp.log')

nanny = Client("nanny", **nanny_params)

app = Flask(__name__)
RoutingController.register(app)
Service.register(app)


if __name__ == '__main__':
    print(app.url_map)
    app.run(port=os.getenv("FLASK_PORT", 5000), host="0.0.0.0")
