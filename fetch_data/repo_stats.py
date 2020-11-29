
def get_last_year_commits(repo):
    commit_activities = repo.get_stats_commit_activity()
    # last_years_commits = 0
    # Alle Commits der letzten 12 Monate zusammenzählen
    # if commit_activities != None:
    #     for week in commit_activities:
    #         last_years_commits += week.total
    return [a.raw_data for a in commit_activities]
