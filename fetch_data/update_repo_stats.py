from github import Github, RateLimitExceededException
import os
import logging
import pickle
import traceback

from time import sleep
import datetime

from repo_stats import get_last_year_commits

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

g = Github(os.environ['GITHUBTOKEN'])

state = {}

def retry(func, repo, retry=2):
    error_list = []
    for i in range(retry):
        try:
            return func(repo)
        except RateLimitExceededException:
            raise
        except Exception as err:
            traceback.print_exc()
            logger.info(f'failed with repo: {repo.name} retrying ({i} of 9)')
            error_list.append(err)
    return error_list


def load_state():
    with open('data/retro_stats.pickle', 'rb') as file:
        state = pickle.load(file)
    return state


def save_to_file(name, state):
    with open(f'data/{name}.pickle', 'wb') as file:
        pickle.dump(state, file)


def handle_rate_limit():
    reset_time = datetime.datetime.fromtimestamp(g.rate_limiting_resettime)
    logger.warning(f'rate limit exceeded, continuing on {reset_time}')
    while datetime.datetime.now() < reset_time:
        sleep(20)


def get_repo_info(repo_name):
    while True:
        try:
            repo = g.get_repo(repo_name)
            repo_data = {
                "name": repo.name,
                "url": repo.html_url,
                "fork": repo.fork,
                "num_forks": repo.forks_count,
                "num_contributors": retry(
                    lambda repo: repo.get_contributors().totalCount,
                    repo
                ),
                "num_commits": retry(
                    lambda repo: repo.get_commits().totalCount,
                    repo
                ),
                "num_stars": repo.stargazers_count,
                "num_watchers": repo.subscribers_count,
                "commit_activities": retry(get_last_year_commits, repo),
                "issues_closed": retry(
                    lambda repo: repo.get_issues(state="closed").totalCount,
                    repo
                ),
                "issues_all": retry(
                    lambda repo: repo.get_issues(state="all").totalCount,
                    repo
                ),
                "pull_requests_closed": retry(
                    lambda repo: repo.get_pulls(state="closed").totalCount,
                    repo
                ),
                "pull_requests_all": retry(
                    lambda repo: repo.get_pulls(state="all").totalCount,
                    repo
                ),
                "comments": retry(
                    lambda repo: repo.get_comments().totalCount,
                    repo
                )
            }
        except RateLimitExceededException:
            handle_rate_limit()
            traceback.print_exc()
        else:
            break
    return repo_data


def main():
    state = load_state()
    print(state)
    counter = 0
    for repo in state['repos']:
        logger.info(repo['full_name'])
        repo_info = get_repo_info(repo['full_name'])
        state['repos'].append(repo_info)
        counter += 1
        if counter >= 10:
            counter = 0
            save_to_file('auto_save_update', state)


if __name__ == "__main__":
    try:
        main()
    except:
        try:
            with open('data/crash/update_repo-crash.pickle', 'wb') as file:
                pickle.dump(state, file)
        except:
            with open('crash.pickle', 'wb') as file:
                pickle.dump(state, file)
        logger.info('state saved in data')
        raise
    else:
        save_to_file('repo_stats', state)

