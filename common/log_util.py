import json
import logging
import collections
from logging.config import dictConfig

## 공통로그 생성
def logger_initialize(file=None):
    if file is None:
        file = 'logger_setting.json'
    logger = common_logger(file)
    global logger
    
def common_logger(file):
    ## 환경 세팅 - JSON 파일로 부터 처리
    with open(file) as fp:
        logging_config = json.load(fp)
        ## 버전 항목, RotatingFileHandler의 backupCount
        dictConfig(logging_config)
        return logging.getLogger()
## 로그 남기기, 얻어온 공통로그와 로그레벨을 이용하여 로그 처리
def log(messages,level=None):
    if type(messages) != str and isinstance(messages,collections.Iterable):
        messages = ' :: '.join([str(m) for m in messages])
    if level is None:
        level = logging.DEBUG
    if level == logging.DEBUG:
        logger.debug(messages)
    elif level == logging.INFO:
        logger.info(messages)
    elif level == logging.WARNING:
        logger.warning(messages)
    elif level == logging.ERROR:
        logger.error(messages)
    else:
        print("$$ Check :",messages)