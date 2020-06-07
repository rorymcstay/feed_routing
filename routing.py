import logging
from logging.config import dictConfig
import os

from feed.settings import nanny_params, logger_settings_dict

from feed.service import Client


if __name__ == '__main__':
    logging.getLogger('conn').setLevel('WARNING')
    logging.getLogger('urllib').setLevel('WARNING')
    logging.getLogger('parser').setLevel('WARNING')
    logging.getLogger('metrics').setLevel('WARNING')
    logging.getLogger('connectionpool').setLevel('WARNING')
    logging.getLogger('kafka').setLevel('WARNING')
    logging.getLogger('config').setLevel('WARNING')
    dictConfig(logger_settings_dict('root'))

    from src.main.app import app
    logging.info("\n".join([f'{key}={os.environ[key]}' for key in os.environ]))
    logging.info(app.url_map)
    app.run(port=os.getenv("FLASK_PORT", os.getenv("ROUTING_PORT", 5002)), host=os.getenv('ROUTER_HOST', 'localhost'))

