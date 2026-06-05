import logging
from logging.handlers import TimedRotatingFileHandler
import os

# Create the logs folder if it does not exist
if not os.path.exists("logs"):
    os.makedirs("logs")

logger = logging.getLogger("api_logger")
logger.setLevel(logging.INFO)

# TimedRotatingFileHandler creates a new file every day at midnight
handler = TimedRotatingFileHandler(
    filename="logs/app.log",
    when="midnight",
    interval=1,
    backupCount=30,
    encoding="utf-8"
)

# Format the log message according to the requirements
formatter = logging.Formatter('%(levelname)s | %(asctime)s | %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
