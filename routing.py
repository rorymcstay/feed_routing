import logging
from logging.config import dictConfig
import os

from feed.settings import nanny_params

from feed.service import Client


nanny = Client("nanny", **nanny_params)





if __name__ == '__main__':
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s]%(thread)d: %(module)s - %(levelname)s - %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })
    from src.main.app import app
    logging.info("\n".join([f'{key}={os.environ[key]}' for key in os.environ]))
    logging.info(app.url_map)
    app.run(port=os.getenv("FLASK_PORT", os.getenv("ROUTING_PORT", 5003)), host=os.getenv('ROUTER_HOST'))

