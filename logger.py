import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S", style='%')
stream_formatter = logging.Formatter(fmt="%(asctime)s %(message)s", datefmt="%H:%M:%S", style='%')

file_handler = logging.FileHandler("/Users/jasonstayner/Python/Chat_Room/server_log.log")
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(stream_formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)