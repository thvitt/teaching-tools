#!/usr/bin/env python3

import argparse
from glob import glob
from pathlib import Path
from difflib import SequenceMatcher
from itertools import combinations
import pandas as pd
import scipy.cluster.hierarchy as sch
import sys
from tqdm import tqdm
from .unify_source import load_unified_source
from matplotlib import pyplot as plt
import scipy.spatial.distance as ssd
try:
    import seaborn as sns
except ImportError:
    pass


def getargparser():
    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                description="Finds similar python scripts")
    p.add_argument("-p", "--pattern", default="*.py", help="glob pattern which files to check")
    p.add_argument("-d", "--dendrogram", nargs='?', const="(show)", help="generate and optionally save a dendrogram")
    p.add_argument("-H", "--headings", nargs='?', const=sys.stdout, type=argparse.FileType("wt", encoding="UTF-8"),
                   help="Write a headings file with group headings")
#    p.add_argument("-s", "--similarities", nargs='?', const=sys.stdout, type=argparse.FileType("wt", encoding="UTF-8"),
#                   help="Write a file with individual similarities"),
    p.add_argument("-t", "--threshold", nargs=1, default=0.1, type=float,
                   help="Similarity threshold")
    return p

def load(files) -> pd.Series:
    return pd.Series(data=[load_unified_source(file, copy_unparseable=True)
                               for file in tqdm(files, desc="Reading files")],
                         index=[str(Path(file).name).split('_')[0] for file in files])

def distance_matrix(contents: pd.Series):
    n = len(contents.index)
    diffs=pd.DataFrame(index=contents.index, columns=contents.index).fillna(0)

    for i, j in tqdm(combinations(contents.index, 2), desc='Calculating distances'):
        delta = 1-SequenceMatcher(a=contents.loc[i], b=contents.loc[j]).quick_ratio()
        diffs.loc[i,j] = delta
        diffs.loc[j,i] = delta
    return diffs

def cluster(diffs: pd.DataFrame, threshold: float):
    dist_vect = ssd.squareform(diffs, force="tovector")
    clustering = sch.ward(dist_vect)
    flattened = pd.Series(index=diffs.index, data=sch.fcluster(clustering, threshold*max(dist_vect), 'distance'))
    groups = flattened.groupby(flattened).groups.values()
    return clustering, groups

def dendrogram(clustering, labels, output, threshold):
    dend = sch.dendrogram(clustering, orientation='left', labels=labels, color_threshold=threshold)
    if output == "(show)":
        plt.show()
    else:
        plt.savefig(output)

def write_headings(groups, output):
    for group in groups:
        output.write('## ' + "; ".join(group) + '\n\n')

def list_collabs(groups):
    collabs = [group for group in groups if len(group) > 1]
    print(f'{len(collabs)} out of {len(groups)} solutions might be collaborations:')
    for group in collabs:
        print('-', ', '.join(group))


def main():
    options = getargparser().parse_args()
    contents = load(glob(options.pattern))
    diffs = distance_matrix(contents)
    clustering, groups = cluster(diffs, options.threshold)
    if options.dendrogram:
        dendrogram(clustering, contents.index, options.dendrogram, options.threshold)
    if options.headings:
        write_headings(groups, options.headings)
    list_collabs(groups)


if __name__ == '__main__':
    main()


# files = list(Path().glob('*.py'))
# dend = sch.dendrogram(clustering, orientation='left', labels=contents.index, color_threshold=0.1)
#
# print(diffs)
#
# for who in diffs.index:
#     col = diffs[who]
#     print('###', who, '\n', col[col < 0.1], '\n')
#
#
#
# dend = sch.dendrogram(clustering, orientation='left', labels=contents.index, color_threshold=0.1)
# plt.savefig('dendrogram.pdf')
# plt.show()
