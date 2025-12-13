import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-40s | %(levelname)-8s | %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S",
)


def get_logger(name):
    return logging.getLogger(name)
