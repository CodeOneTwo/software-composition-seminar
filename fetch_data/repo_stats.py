from decorators import retry

@retry
def get_commit_activities(repo):
    commit_activities = repo.get_stats_commit_activity()
    return [a.raw_data for a in commit_activities]

@retry
def date_of_last_commit(repo):
    last_commit = repo.get_commits()[0]
    last_commit.last_modified

@retry
def get_feature_files(repo, g):
    files = g.search_code(query=f'repo:{repo.full_name} extension:feature')
    return [ file.path for file in files ]

@retry
def contains_cucumber(repo, g):
    files = g.search_code(query=f'repo:{repo.full_name} Cucumber')
    return [ file.path for file in files ]

@retry
def contains_given(repo, g):
    files = g.search_code(query=f'repo:{repo.full_name} Cucumber')
    return [ file.path for file in files ]

@retry
def get_languages(repo):
    return repo.get_languages()

@retry
def get_commits_with_given(repo, g):
    files = g.search_commits(query=f'repo:{repo.full_name} Given')
    return files.totalCount
