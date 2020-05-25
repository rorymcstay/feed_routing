from flask import Flask
from src.main.manager import RoutingController
from src.main.domain import FeedHistory
from feed.service import Service
from feed.chainsessions import init_app

app = init_app(FeedHistory)

RoutingController.register(app)
Service.register(app)

