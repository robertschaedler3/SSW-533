from datetime import datetime
import os

import pandas as pd
import numpy as np

from pydriller import RepositoryMining

import matplotlib.pyplot as plt
import ruptures as rpt
    
import fire

GITHUB = 'https://github.com'

def repo_data(repo, start, end):
    commit_data = []
    for commit in RepositoryMining(f'{GITHUB}/{repo}', since=start, to=end).traverse_commits():
        commit_data.append([
            commit.hash,
            commit.author_date,
            commit.committer_date,
            commit.insertions,
            commit.deletions,
            commit.lines,
            commit.files
        ])
    
    df = pd.DataFrame(data=commit_data, columns=['hash', 'author_date', 'committer_date', 'insertions', 'deletions', 'lines', 'files'])
    df['committer_date'] = pd.to_datetime(df['committer_date'], utc=True)

    return df

def change_point_detection(data):
    # Create 'signal' for change point detection
    signal = data.values

    n_bkps = 1

    algo = rpt.Dynp(model="l2").fit(signal)
    bkps = algo.predict(n_bkps=n_bkps)
    bkps[-1] -= 1

    return bkps


def run(repos, start, end):

    fig, ax = plt.subplots(len(repos), figsize=(12, 8))

    for i, repo in enumerate(repos):
        data = repo_data(repo, start, end)

        # Group commits by day
        data = data.groupby(pd.Grouper(key='committer_date', freq='1D')).sum()

        # Reindex to fill missing days
        idx = pd.date_range(data.index[0], data.index[-1])

        data.index = pd.DatetimeIndex(data.index)
        data = data.reindex(idx, fill_value=0)

        # Re-Group by month (30 days)
        data.index = data.index.rename('committer_date')
        data.reset_index(inplace=True)
        data = data.groupby(pd.Grouper(key='committer_date', freq='30D')).sum()

        # Save
        data.to_csv(os.path.join(os.getcwd(), repo.replace('/', '_')))

        # Run change point detection on data
        bkps = change_point_detection(data)
        for bkp in bkps[:-1]:
            print(f'{((repo[:20] + "...") if len(repo) > 23 else repo[:23]):<23} | {data.index[bkp]}')

        # Add data to plot
        ax[i].title.set_text(repo)

        for col in data.columns:
            ax[i].plot(data.index, data[col])
        
        # Highlight breakpoints
        prev_bkp, color = 0, 'green'
        for bkp in bkps:
            start_index, end_index = data.index[prev_bkp], data.index[bkp]
            ax[i].axvspan(start_index, end_index, color=color, alpha=0.2)
            prev_bkp = bkp
            color = 'red' if color == 'green' else 'green'

        if i != len(repos) - 1:
            plt.setp(ax[i].get_xticklabels(), visible=False)

        fig.show()


def run(*repos, start=None):

    if start == None:
        start = datetime(2018, 1, 1)
    else: 
        start = datetime.strptime(start, '%d/%m/%Y')
    
    repos(list(repos), start, datetime.now())
    


if __name__ == '__main__':
    fire.Fire(run)