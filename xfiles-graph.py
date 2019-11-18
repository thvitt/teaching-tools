import sys
from itertools import chain
from os import fspath

import networkx as nx
from pathlib import Path
from lxml import etree

ns = {'p': "http://www.w3.org/ns/xproc",
      'xsl': 'http://www.w3.org/1999/XSL/Transform'}

paths = {'//xsl:import/@href': 'import',
         '//xsl:include/@href': 'include',
         '//p:import/@href': 'pipeline',
         '//p:xslt/p:input[@port="stylesheet"]/p:document/@href': 'xslt'}


class Analyzer:

    def __init__(self, path: Path):
        self.g = nx.DiGraph()
        self.seen = set()
        self.root = path.resolve() if path.is_dir() else path.resolve().parent
        self.analyze_dir(path)

    def analyze_dir(self, root: Path):
        if root.is_dir():
            for file in chain(root.glob('**/*.xpl'), root.glob('**/*.xsl')):
                self.analyze_path(file)
        else:
            self.analyze_path(root)

    def analyze_path(self, file: Path):
        if file in self.seen:
            return
        self.seen.add(file)
        if not file.exists():
            print(file, 'does not exist')
            return
        self.g.add_node(file)
        tree = etree.parse(fspath(file))
        for path, label in paths.items():
            for href in tree.xpath(path, namespaces=ns):
                target: Path = file.parent / href
                target_label = target.resolve().relative_to(self.root)
                if target.exists():
                    self.g.add_edge(file, target_label, label=label)
                    self.analyze_path(target)

    def to_dot(self):
        nx.nx_agraph.write_dot(self.g, 'imports.dot')


if __name__ == '__main__':
    Analyzer(Path(sys.argv[1])).to_dot()
