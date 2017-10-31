from __future__ import absolute_import, division, print_function

import importlib
import os
import pkgutil
import sys


def find_package_path(package_str):
    """
    Attempts to find the path to a given package provided the root package is
    already on the path.

    :param package_str: Package to search for as a Python path (i.e.
                        "mantidimaging.core.filters")

    :return: Path to package
    """
    package_as_path = os.sep.join(package_str.split('.'))
    for path in sys.path:
        candidate_path = os.path.join(path, package_as_path)
        if os.path.exists(candidate_path):
            return candidate_path

    raise RuntimeError("Cannot find path for package {}".format(package_str))


def get_package_children(package_name, packages=False, modules=False,
                         ignore=None):
    """
    Gets a list of names of child packages or modules found under a given
    package.

    :param package: The package to search within

    :param packages: Set to True to return packages

    :param modules: Set to True to return modules

    :param ignore: List of explicitly matching modules to ignore

    :return: Iterator over matching modules
    """
    # Walk the children (packages and modules) of the provided root package
    pkgs = pkgutil.walk_packages([find_package_path(package_name)],
                                 prefix=package_name + '.')

    # Ignore those that do not match the package/module selection criteria
    pkgs = filter(lambda p: p[2] and packages or not p[2] and modules, pkgs)

    # Ignore moduels that we want to ignore
    if ignore:
        pkgs = filter(lambda p: not any([m in p[1] for m in ignore]),
                      pkgs)

    return pkgs


def import_items(names, required_attributes=None):
    """
    Imports a list of packages/modules and filters out those that do not have a
    specified required list of attributes.

    :param names: List of package/module names to import

    :param required_attributes: Optional list of attributes that must be
                                present on each individual module

    :return: List of imported packages/modules
    """
    imported = [importlib.import_module(n) for n in names]

    # Filter out those that do not contain all the required attributes
    if required_attributes:
        imported = filter(
                lambda i: all([hasattr(i, a) for a in required_attributes]),
                imported)

    return imported


def register_into(items, container, func):
    """
    Registers a list of packages and/or modules into a containing instance.

    :param items: List of packages/modules to register

    :param container: Container (instance) to register them into

    :param func: Function by which packages/modules are registered into the
                 container
    """
    for m in items:
        func(container, m)