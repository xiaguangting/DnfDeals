import logging
from logging.handlers import TimedRotatingFileHandler

from DnfDeals import settings

hunter = logging.Logger(name='hunter')

handler = TimedRotatingFileHandler(filename=settings.LOG_ADDRESS, when='D', backupCount=30)
hunter.addHandler(handler)
