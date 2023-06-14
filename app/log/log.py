import logging
from logging import StreamHandler, FileHandler


def logger():

    stream_handler = StreamHandler()

    file_handler = FileHandler(filename='log.log', mode='a',)
    file_handler.setLevel(logging.WARNING)

    log_format = '%(levelname)s - %(asctime)s - %(filename)s:%(lineno)s - %(message)s'

    logging.basicConfig(level=logging.INFO,
                        format=log_format,
                        handlers=[stream_handler,
                                  file_handler,
                                  ]
                        )

    return logging.getLogger()
