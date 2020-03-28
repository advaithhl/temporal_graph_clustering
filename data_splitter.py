import csv
from datetime import datetime, timedelta
from os import mkdir
from subprocess import run

import pandas as pd

# Dataset specific details
from dirs import SPLIT_DIR

SRC_FILE = 'CollegeMsg.txt'
DIFF_DAYS = 1
START = 1082040961
FINISH = 1098777142


def numbers():
    """ Yield natural numbers continuously. """
    global cnt
    cnt = 0
    while True:
        cnt += 1
        yield cnt


def getnodes(partno, out_dir=SPLIT_DIR):
    """ Return the static node labels of part number. """
    filename = f'{out_dir}/nodes.csv'
    try:
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            for (idx, data) in enumerate(reader, start=1):
                if idx == partno:
                    return data
    except FileNotFoundError:
        print(f'Node data not found. Have you split the dataset?')


def split_dataset(src_file=SRC_FILE, diff_days=DIFF_DAYS, start=START,
                  finish=FINISH, out_dir=SPLIT_DIR):
    """
    Split the dataset into multiple parts.

    Params
    ------
    src_file: path of the dataset to be split.
    diff_days: number of days needed in each part.
    start: UNIX time when first message was sent.
    finish: UNIX time when last message was sent.
    out_dir: directory to which the split dataset should be written.
    """
    # Find start date as datetime object.
    start_timestamp = start
    start_datetime = datetime.fromtimestamp(start_timestamp)

    # Set diff as timedelta of DIFF_DAYS provided.
    diff = timedelta(days=diff_days)

    # Delete old directory and made new directory.
    result = run(['rm', '-r', out_dir])
    if result.returncode == 0:
        print('Removed old datafiles.')
    mkdir(out_dir)

    # Read the entire dataset as a pandas Dataframe.
    df = pd.read_csv(src_file, sep=' ')
    print('Creating new datafiles.')
    lengths = []
    nodes = []

    # Filter dataframe based on time ranges, creating new files for each range.
    # Gather all unique nodes of each part.
    for i in numbers():
        end_datetime = start_datetime + diff
        end_timestamp = datetime.timestamp(end_datetime)
        temp = df[(df.time >= start_timestamp) & (df.time < end_timestamp)]
        if start_timestamp < finish:
            lengths.append(len(temp))
            nodes.append(set(temp.src))
            nodes[-1].update(temp.dst)
            temp.to_csv(f'{out_dir}/part{i:03}.txt', sep=' ',
                        index=False, header=False)
            start_timestamp, start_datetime = end_timestamp, end_datetime
        else:
            print(f'Temporal data split complete!')
            break

    # Write each part as lines in nodes.csv in output directory.
    with open(f'{out_dir}/nodes.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(nodes)
    print(f'Wrote node data to {out_dir}/nodes.csv')
    print('\nStats')
    print('-----')
    print(f'Parts                       : {cnt - 1}')
    print(f'Message span in each part   : {diff_days} day(s)')
    print(f'Shortest part length        : {min(lengths)}')
    print(
        'Shortest part(s)            : '
        f'{[i for i, l in enumerate(lengths, start=1) if l == min(lengths)]}')
    print(f'Longest part length         : {max(lengths)}')
    print(
        'Longest part(s)             : '
        f'{[i for i, l in enumerate(lengths, start=1) if l == max(lengths)]}')
    print(
        'Average length of each part : '
        f'{round(sum(lengths) / len(lengths), 2)}')


if __name__ == '__main__':
    split_dataset()
