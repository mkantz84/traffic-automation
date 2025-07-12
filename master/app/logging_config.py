import logging

def setup_logging():
    logging.basicConfig(
        level=logging.WARN,
        format='[%(levelname)s] %(asctime)s %(name)s: %(message)s'
    ) 