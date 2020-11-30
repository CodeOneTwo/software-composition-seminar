from github import Github, RateLimitExceededException
import os
import logging
import pickle
import traceback

from time import sleep
import datetime

from repo_stats import get_commit_activities, get_feature_files, get_languages, get_commits_with_given, date_of_last_commit, contains_cucumber, contains_given
from decorators import retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

g = Github(os.environ['GITHUBTOKEN'])

state = {}


def load_state():
    with open('data/repo_stats.pickle', 'rb') as file:
        state = pickle.load(file)
    return state


def save_to_file(name, state):
    with open(f'data/{name}.pickle', 'wb') as file:
        pickle.dump(state, file)


@retry
def update_repo_info(repo_data):
    repo = g.get_repo(repo_data['full_name'])
    # repo_data["name"] = repo.name
    # repo_data["full_name"] = repo.full_name
    # repo_data["url"] = repo.html_url
    # repo_data["fork"] = repo.fork
    # repo_data["num_forks"] = repo.forks_count
    # repo_data["num_contributors"] = retry(
    #     lambda repo: repo.get_contributors().totalCount
    # )(repo)
    # repo_data["num_commits"] = retry(
    #     lambda repo: repo.get_commits().totalCount
    # )(repo)
    # repo_data["num_stars"] = repo.stargazers_count
    # repo_data["num_watchers"] = repo.subscribers_count
    # repo_data["commit_activities"] = get_commit_activities(repo)
    # repo_data["issues_closed"] = retry(
    #     lambda repo: repo.get_issues(state="closed").totalCount
    # )(repo)
    # repo_data["issues_all"] = retry(
    #     lambda repo: repo.get_issues(state="all").totalCount
    # )(repo)
    # repo_data["pull_requests_closed"] = retry(
    #     lambda repo: repo.get_pulls(state="closed").totalCount
    # )(repo)
    # repo_data["pull_requests_all"] = retry(
    #     lambda repo: repo.get_pulls(state="all").totalCount
    # )(repo)
    # repo_data["comments"] = retry(
    #     lambda repo: repo.get_comments().totalCount
    # )(repo)
    # repo_data["languages"] = get_languages(repo)
    repo_data["date_of_last_commit"] = date_of_last_commit(repo)
    repo_data["commits_with_given"] = get_commits_with_given(repo, g)
    repo_data["file_cucumber"] = contains_cucumber(repo, g)
    repo_data["file_given"] = contains_given(repo, g)
    repo_data["files_feature"] = get_feature_files(repo, g)


def main():
    state = load_state()
    print(state)
    counter = 0
    for repo in state['repos']:
        logger.info(repo['full_name'])
        update_repo_info(repo)
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
        save_to_file('updated_repo_stats', state)

