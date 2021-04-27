import json
import requests

from datetime import datetime

from pydriller import RepositoryMining

import pandas as pd
import numpy as np


def run(repo, start, end):

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

    print(df)


if __name__ == '__main__':
    start = datetime(2016, 10, 8, 17, 0, 0)
    end = datetime.now()
    run('https://github.com/robertschaedler3/robertschaedler.com', start, end)
