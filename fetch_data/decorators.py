from github import RateLimitExceededException
import traceback
import logging
from time import sleep
import datetime
from github import Github
import os

g = Github(os.environ['GITHUBTOKEN'])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def retry(func, retry=2):
    def wrapper(*args, **kwargs):
        error_list = []
        for i in range(retry):
            try:
                return func(*args, **kwargs)
            except RateLimitExceededException:
                handle_rate_limit()
                traceback.print_exc()
            except Exception as err:
                traceback.print_exc()
                logger.info(f'failed with repo: {args[0].full_name} retrying ({i+1} of 9)')
                error_list.append(err)
        return error_list
    return wrapper


def handle_rate_limit():
    reset_time = datetime.datetime.fromtimestamp(g.rate_limiting_resettime)
    logger.warning(f'rate limit exceeded, continuing on {reset_time}')
    while datetime.datetime.now() < reset_time:
        sleep(20)

