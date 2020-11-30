from github import Github, RateLimitExceededException
import os
import logging
import pickle
import traceback

import datetime

from repo_stats import get_commit_activities, get_feature_files, get_languages, get_commits_with_given, date_of_last_commit, contains_cucumber, contains_given
from decorators import retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

g = Github(os.environ['GITHUBTOKEN'])
state = {
    'repos': []
}


def load_data():
    with open('data/repos.pickle', 'rb') as file:
        repos = pickle.load(file)
    return repos


def save_to_file(name, state):
    with open(f'data/{name}.pickle', 'wb') as file:
        pickle.dump(state, file)



@retry
def get_repo_info(repo_name):
    repo = g.get_repo(repo_name)
    repo_data = {
        "name": repo.name,
        "full_name": repo.full_name,
        "url": repo.html_url,
        "fork": repo.fork,
        "num_forks": repo.forks_count,
        "num_contributors": retry(lambda repo: repo.get_contributors().totalCount)(repo),
        "num_commits": retry(lambda repo: repo.get_commits().totalCount)(repo),
        "num_stars": repo.stargazers_count,
        "num_watchers": repo.subscribers_count,
        "commit_activities": get_commit_activities(repo),
        "issues_closed": retry(
            lambda repo: repo.get_issues(state="closed").totalCount
        )(repo),
        "issues_all": retry(lambda repo: repo.get_issues(state="all").totalCount)(repo),
        "pull_requests_closed": retry(
            lambda repo: repo.get_pulls(state="closed").totalCount
        )(repo),
        "pull_requests_all": retry(
            lambda repo: repo.get_pulls(state="all").totalCount
        )(repo),
        "comments": retry(lambda repo: repo.get_comments().totalCount)(repo),
        "languages": get_languages(repo),
        "date_of_last_commit": date_of_last_commit(repo),
        "commits_with_given": get_commits_with_given(repo, g),
        "file_cucumber": contains_cucumber(repo, g),
        "file_given": contains_given(repo, g),
        "files_feature": get_feature_files(repo, g),
    }
    return repo_data


def main():
    repos = load_data().values()
    print(repos)
    counter = 0
    for repo_name in repos:
        logger.info(repo_name)
        repo_info = get_repo_info(repo_name)
        state['repos'].append(repo_info)
        counter += 1
        if counter >= 10:
            counter = 0
            save_to_file('auto_save', state)


if __name__ == "__main__":
    try:
        main()
    except:
        try:
            with open('data/crash/fetch_data-crash.pickle', 'wb') as file:
                pickle.dump(state, file)
        except:
            with open('crash.pickle', 'wb') as file:
                pickle.dump(state, file)
        logger.info('state saved in data')
        raise
    else:
        save_to_file('repo_stats', state)

