import logging
from logging.config import dictConfig
import os

from feed.settings import nanny_params, logger_settings_dict

from feed.service import Client


nanny = Client("nanny", **nanny_params)





if __name__ == '__main__':
    dictConfig(logger_settings_dict)
    from src.main.app import app
    logging.info("\n".join([f'{key}={os.environ[key]}' for key in os.environ]))
    logging.info(app.url_map)
    app.run(port=os.getenv("FLASK_PORT", os.getenv("ROUTING_PORT", 5002)), host=os.getenv('ROUTER_HOST', 'localhost'))

