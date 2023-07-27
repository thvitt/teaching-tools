#!/usr/bin/env python3

#FIXME needs refactoring

"""
Creates a file sampled from words according to a spec.

Synopsis:

    mix-words (factor | string | filename)+ [k] > output.txt 
              `---------- spec -----------´

Description:

    spec - specification of the mix of the output words
    k -    absolute number of words in the output file.

    The specification is composed of an arbitrary sequence of numbers, strings
    and filenames.

    A number will set the current mix factor (the default is 1.0). A filename
    argument will read and tokenize the given file. A string argument will be
    tokenized. For each non-number argument, the current factor will be
    distributed among the tokens resulting from that argument and used as a weight.
    A final number specifies the total number of words to sample.

    The script will write the generated text to stdout and a statistic to stderr.

Examples:

    $ mix-words foo 2 bar baz 100

    generates 100 words of which approx. 20% will be 'foo', 40% 'bar' and 40%
    'baz'.

    $ mix-words 0.8 top100.txt 0.1 New 0.05 York Orleans 5000

    generates 5000 words, of which 80% will come from the file top100.txt, 10%
    will be 'New', and 'York' and 'Orleans' will each make up 5% of the result. 
"""

import sys
from pathlib import Path
import re
from typing import Counter, cast
import random
from operator import itemgetter

def main():
    population = []
    weights = []
    spec = list(reversed(sys.argv[1:]))
    final_spec = []
    if not spec:
        print(__doc__)
        sys.exit(1)
    else:
        arg = '!!!'
        factor = 1.0
        while spec:
            arg: str = spec.pop()
            try:
                factor = float(arg)
            except ValueError:
                if Path(arg).is_file():
                    text = Path(arg).read_text()
                    final_spec.append((' ' + arg, factor))
                else:
                    text = arg 
                    final_spec.append((arg, factor))

                tokens = cast(list[str], re.findall(r'\w+', text))
                factor_by_token = factor / len(tokens)
                population.extend(tokens)
                weights.extend([factor_by_token] * len(tokens))

        try:
            k = int(arg)
        except ValueError:
            k = len(population) * 100

        result = random.choices(population, weights=weights, k=k)

        factor_weights = sum(map(itemgetter(1), final_spec))
        print(f"Spec: {k} words, mix:", " • ".join(f'{weight / factor_weights:2.1%} {source}'
            for source, weight in final_spec), file=sys.stderr)
        print("Sampled distribution:", file=sys.stderr)
        stat_len = max(10, len(final_spec) + 5)

        stats_ = Counter(result).most_common()
        others = sum(map(itemgetter(1), stats_[stat_len:]))
        stats = stats_[:stat_len] + [('*', others)]
        for token, count in stats:
            fraction = count / k
            bar = "━" * int(50*fraction)
            print(f"{bar:>50} {count:5d} {fraction:5.1%} {token[:40]}", file=sys.stderr)
        print(' '.join(result))
