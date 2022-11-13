#!/usr/bin/env python3

import astor
import ast
import sys
from collections import defaultdict
from itertools import count
from functools import partial
import logging

logger = logging.Logger(__name__)


def name_map(fmt="v{}", start=0):
    """
    Creates a mapping that can map existing values to artificial names.

    Args:
           fmt (str): Format string with one numeric variable
           start (int): First index used by the mapping

    Example:
        >>> names = name_map()
        >>> names['foo']
        'v0'
        >>> names['bar']
        'v1'
        >>> names['foo']
        'v0'
    """
    return defaultdict(partial(next, (fmt.format(i) for i in count(start))))


class Renamer(ast.NodeVisitor):
    def __init__(self):
        self.new_names = name_map()

    def visit_Name(self, node):
        node.id = self.new_names[node.id]
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        node.name = self.new_names[node.name]
        self.generic_visit(node)


def load_unified_source(filename: str, copy_unparseable: bool = False) -> str:
    try:
        code = astor.code_to_ast.parse_file(filename)
        Renamer().visit(code)
        return astor.to_source(code)
    except:
        logger.error("Failed to parse {}".format(filename), exc_info=True)
        if copy_unparseable:
            with open(filename, "rt") as source:
                return source.read()
        else:
            raise


def main():
    print(load_unified_source(sys.argv[1]))


if __name__ == '__main__':
    main()
