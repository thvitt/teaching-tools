#!/usr/bin/env python3

from pathlib import Path
from difflib import SequenceMatcher
from itertools import combinations
import pandas as pd
import scipy.cluster.hierarchy as sch
from tqdm import tqdm
from unify_source import load_unified_source
from matplotlib import pyplot as plt
import scipy.spatial.distance as ssd
try:
    import seaborn as sns
except ImportError:
    pass


files = list(Path().glob('*.py'))
contents = pd.Series(data=[load_unified_source(str(file))
                           for file in tqdm(files, desc="Reading files")],
                     index=[str(file.name).split('_')[0] for file in files])
n = len(files)
diffs=pd.DataFrame(index=contents.index, columns=contents.index).fillna(0)

for i, j in tqdm(combinations(contents.index, 2), desc='Calculating distances'):
    delta = 1-SequenceMatcher(a=contents.loc[i], b=contents.loc[j]).quick_ratio()
    diffs.loc[i,j] = delta
    diffs.loc[j,i] = delta


print(diffs)

for who in diffs.index:
    col = diffs[who]
    print('###', who, '\n', col[col < 0.1], '\n')

dist_vect = ssd.squareform(diffs, force="tovector")
clustering = sch.ward(dist_vect)
flattened = pd.Series(index=diffs.index, data=sch.fcluster(clustering, 0.1*max(dist_vect), 'distance'))
for group in flattened.groupby(flattened).groups.values():
    print('## ', "; ".join(group), end='\n\n')

dend = sch.dendrogram(clustering, orientation='left', labels=contents.index, color_threshold=0.1)
plt.savefig('dendrogram.pdf')
plt.show()
