from app import create_app

app = create_app()


import logging
from logging.handlers import RotatingFileHandler
import os

if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/error.log', maxBytes=10240, backupCount=10)
file_handler.setLevel(logging.ERROR)
app.logger.addHandler(file_handler)
