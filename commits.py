from datetime import datetime

import pandas as pd
import numpy as np

from pydriller import RepositoryMining


def change_point_detection():
    pass


def commit_data(repo, start, end):

    commit_data = []

    for commit in RepositoryMining(repo, since=start, to=end).traverse_commits():
        commit_data.append([commit.hash,
                            commit.author_date,
                            commit.committer_date,
                            commit.insertions,
                            commit.deletions,
                            commit.lines,
                            commit.files])

        # Temp break for testing
        if len(commit_data) > 10:
            break

    df = pd.DataFrame(data=commit_data, columns=['hash', 'author_date', 'committer_date', 'insertions', 'deletions', 'lines', 'files'])
    df['committer_date'] = pd.to_datetime(df['committer_date'], utc=True)
    # df.set_index('committer_date', inplace=True)
    return df


def run(repo, start, period=1):

    df = commit_data(repo, start, datetime.now())
    print(df.tail())

    sloc = []
    print(df.groupby(by=df['committer_date'].dt.date).sum())
    
    
if __name__ == '__main__':
    start = datetime(2016, 10, 8, 17, 0, 0)
    period = 2  # days for sloc/unit time
    run('https://github.com/robertschaedler3/robertschaedler.com', start, period)
