from __future__ import annotations

from operator import attrgetter
from typing import List, Iterable, Set, Optional, Dict, Callable
from warnings import warn

import re
import apt
import apt_pkg
from blessings import Terminal
from more_itertools import first
from tqdm import tqdm
import operator

t = Terminal()
_operation_labels = dict(
        delete=t.red('✘'),
        downgrade=t.yellow('↓'),
        install=t.green('+'),
        keep=' ',
        reinstall=t.green('↺'),
        upgrade=t.blue('↑'))


def show_pkg(pkg: apt.Package, matcher: Optional[VersionMatcher] = None):
    mark = operation(pkg)
    versions = pkg.installed.version
    if pkg.installed != pkg.candidate:
        versions += '→' + t.green(pkg.candidate.version)
    return _operation_labels[mark] + t.bold(f" {pkg.name:<20}") + f" {versions:<25} {pkg.candidate.summary}"


def operation(pkg):
    return first(attr for attr in _operation_labels if getattr(pkg, 'marked_' + attr, False))


def to_dict(pkg: apt.Package) -> Dict[str, str]:
    return dict(
            name=pkg.name,
            operation=operation(pkg),
            installed=pkg.installed.version,
            candidate=pkg.candidate.version,
            summary=pkg.candidate.summary
    )


def mark_from_dict(descriptor: Dict[str, str], cache: apt.Cache, auto_fix: bool = True) -> apt.Package:
    pkg = cache[descriptor['name']]
    if descriptor['operation'] == 'delete':
        pkg.mark_delete(auto_fix=auto_fix)
    elif pkg.candidate.version != descriptor['candidate']:
        pkg.candidate = first(v for v in pkg.versions if v.version == descriptor['candidate'])
        pkg.mark_install(auto_fix=auto_fix, from_user=not pkg.is_auto_installed)
    return pkg


def relevant_version(version: apt.package.Version) -> bool:
    return any(origin.label.startswith("Unofficial") for origin in version.origins)


def _v(v: apt.package.Version) -> str:
    return f"{v.version} ({v.policy_priority})"


class Plans:
    _properties = ['install', 'upgrade', 'downgrade', 'delete', 'reinstall']  # keep is boring

    def __init__(self, packages: Optional[Iterable[apt.Package]] = None):
        for prop in self._properties:
            setattr(self, prop, set())

        if packages:
            for pkg in packages:
                for prop in self._properties:
                    if getattr(pkg, 'marked_' + prop):
                        getattr(self, prop).add(pkg)

    def __getitem__(self, item):
        if item in self._properties:
            return getattr(self, item)
        else:
            raise KeyError(f"Unknown property: " + item)

    def __setitem__(self, key, value):
        if key in self._properties:
            setattr(self, key, value)
        else:
            raise KeyError(f"Unknown property: " + key)

    def apply_all(self, function, other: Plans):
        if not isinstance(other, Plans):
            raise TypeError('can only compare with other plans object')
        result = Plans()
        for prop in self._properties:
            if callable(function):
                result[prop] = function(self[prop], other[prop])
            else:
                result[prop] = getattr(self[prop], function)(other[prop])
        return result

    def __sub__(self, other: Plans):
        return self.apply_all(operator.sub, other)

    @staticmethod
    def _fmt_pkg(pkg: apt.Package) -> str:
        result = t.underline(pkg.name)
        if pkg.installed and pkg.candidate and pkg.installed != pkg.candidate:
            result += f' {pkg.installed.version} -> {pkg.candidate.version}'
        return result

    def __str__(self):
        result = []
        for prop in self._properties:
            if self[prop]:
                result.append(t.bold(prop) + ":\t" + ", ".join(self._fmt_pkg(pkg) for pkg in self[prop]))
        return '\n'.join(result)

    def to_dict(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Creates a serializable dictionary containing this Plans object's plans.

        Returns:
            The root dictionary has a key for every operation for which there are plans. Each operation's value
            is a list with the affected packages. Each entry in the list is a dictionary mapping package name to
            respective version.
        """
        result = {}
        for prop in self._properties:
            items = []
            for pkg in self[prop]:
                items.append({pkg.name: pkg.candidate.version if pkg.candidate else pkg.installed.version})
            if items:
                result[prop] = items
        return result

    @classmethod
    def apply_dict(cls, source: Dict[str, List[Dict[str, str]]], cache: apt.Cache):
        """
        Applies the dict ``source`` to the given cache by trying to prepare (mark) the operations from the dict.

        Args:
            source: Must be of the format that is produced by to_dict
            cache: cache to work on

        Returns:
            a Plans object for the given cache after applying the given
            operations.
        """
        for prop, items in source:
            if prop not in cls._properties:
                warn(f"Skipping unknown property: {prop}")
            else:
                for item, version in items.entries():
                    pkg = cache[item]
                    cands = [v for v in pkg.versions if v.version == version]
                    if cands:
                        pkg.candidate = cands[0]
                    else:
                        warn(f"Version {version} for package {item} not in cache")
                    marker = getattr(pkg, 'mark_{prop}', pkg.mark_install)
                    marker(auto_fix=False)
        return cls(cache)


cache = apt.cache.Cache()


def find_relevant_packages(relevant_version: Callable[[apt.Version], bool], cache: Iterable[apt.Package] = None):
    installed: List[apt.package.Package] = [pkg for pkg in
                                            tqdm(cache or apt.Cache(), desc='Finding installed packages', unit=' pkg',
                                                 leave=False)
                                            if pkg.is_installed]
    relevant: List[apt.package.Package] = [pkg for pkg in
                                           tqdm(installed, desc='Filtering relevant packages', unit=' pkg', leave=False)
                                           if relevant_version(pkg.installed)]
    print(f"{len(relevant)} relevant of {len(installed)} packages.")
    return relevant


class VersionMatcher:

    def __init__(self, *, origin: Optional[Dict[str, str]] = {}, **patterns):
        self.origin_patterns: Dict[str, re.Pattern] = origin and {k: re.compile(v) for k, v in origin.items()}
        self.patterns: Dict[str, re.Pattern] = patterns and {k: re.compile(v) for k, v in patterns.items()}

    def __call__(self, version: apt.Version) -> bool:
        for attr, pattern in self.patterns.items():
            if pattern.search(getattr(version, attr, '')):
                return True
        for attr, pattern in self.origin_patterns.items():
            if any(pattern.search(getattr(origin, attr, '')) for origin in version.origins):
                return True
        return False


def alternative_version(pkg: apt.Package, is_bad: VersionMatcher) -> Optional[apt.package.Version]:
    versions = sorted(pkg.versions, key=attrgetter('policy_priority'), reverse=True)
    return first((v for v in versions if not is_bad(v)), None)


def alternative_versions(is_bad: VersionMatcher, packages: Iterable[apt.Package]) -> List[apt.package.Version]:
    alt = [alternative_version(pkg, is_bad) for pkg in packages]
    return [v for v in alt if v is not None]


def try_mark_downgrades(is_bad: VersionMatcher, cache: Iterable[apt.Package]):
    rel = find_relevant_packages(is_bad, cache)
    alt = alternative_versions(is_bad, rel)
    for cand in alt:
        pkg: apt.Package = cand.package
        pkg.candidate = cand
        pkg.mark_install(auto_fix=False, from_user=not pkg.is_auto_installed)
