
import os
from github import Github, RateLimitExceededException
import pickle
import logging
import traceback
import datetime
from time import sleep

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

g = Github(os.environ['GITHUBTOKEN'])

state = {
    'counter': 0,
    'wanted': {}
}

# Restore
try:
    with open('wanted.pickle', 'rb') as file:
        state = pickle.load(file)
except FileNotFoundError:
    logger.info('no inital file')

def handle_rate_limit():
    reset_time = datetime.datetime.fromtimestamp(g.rate_limiting_resettime)
    logger.warning(f'rate limit exceeded, continuing on {reset_time}')
    while datetime.datetime.now() < reset_time:
        sleep(2)


repos = g.search_repositories(query='stars:>500', sort='stars', order='desc') # initial search
# repos = g.search_repositories(query='stars:500..19995', sort='stars', order='desc')

try:
    while repos.totalCount !=0:
        last_repo = None
        for repo in repos:
            state['counter'] += 1
            while True:
                try:
                    last_repo = repo
                    repo_name = repo.name
                    logger.info(f'process repo: {repo_name}')
                    if ('Gherkin' in repo.get_languages().keys()):
                        state['wanted'][state['counter']] = repo.full_name
                        logger.info(f'found_repo: {repo_name}')
                    break
                except RateLimitExceededException:
                    handle_rate_limit()
                    traceback.print_exc()
                except:
                    raise
        try:
            repos = g.search_repositories(query=f'stars:500..{repo.stargazers_count}', sort='stars', order='desc')
        except RateLimitExceededException:
            handle_rate_limit()
            traceback.print_exc()
            repos = g.search_repositories(query=f'stars:500..{repo.stargazers_count}', sort='stars', order='desc')
except:
    with open(f'crash-{repo.name}.pickle', 'wb') as file:
        pickle.dump(state, file)

with open('wanted.pickle', 'wb') as file:
    pickle.dump(state, file)

