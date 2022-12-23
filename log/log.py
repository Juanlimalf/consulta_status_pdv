import logging

def log():
    log_format = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s'
    logging.basicConfig(filename='.\log\logs.log',
                        filemode='a',
                        level=logging.WARNING,
                        format=log_format)
    return logging.getLogger()

"""
import logging
log_format = '%(asctime)s:%(levelname)s:%(filename)s:%(lineno)s:%(message)s'
logging.basicConfig(filename='log.log',
                    filemode='a',
                    level=logging.DEBUG,
                    format=log_format)
logger = logging.getLogger()
import sys
from loguru import logger
logger.add('log/logs.log', level='DEBUG', format = "{time} {level} {message}")
logger.add(sys.stdout, colorize=True, format="<green>{time}</green> <level>{message}</level>")
logger.add("file_1.log", rotation="500 MB")    # Girar automaticamente um arquivo muito grande
logger.add("file_2.log", rotation="12:00")     # Um novo arquivo é criado todos os dias ao meio-dia
logger.add("file_3.log", rotation="1 week")    # Quando o arquivo é muito antigo, ele é girado 
logger.add("file_X.log", retention="10 days")  # Limpeza depois de algum tempo 
logger.add("file_Y.log", compression="zip")    # Economize algum espaço
#logger.add ('logs / logs.log', level = 'DEBUG', format = "{time} {level} {message}")
"""


