#!/usr/bin/env python

"""

             Name:  show_unused_munki_packages.py
      Description:  Given a path to a Munki repo, this script will tell you
                    which package names are unused in any manifests. Useful for
                    detecting things that were imported into Munki but never
                    added to a manifest.
           Author:  Elliot Jordan <elliot@lindegroup.com>
          Created:  2015-07-30
    Last Modified:  2015-08-03
          Version:  1.0.7

"""

import argparse
import os
import plistlib
import sys
from pprint import pprint
from xml.parsers.expat import ExpatError


def get_repo():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='Please Specify the path to your munki repo. /Users/munki_repo')
    args = parser.parse_args()
    return args.path


def process_manifest(manifest, packages_in_manifests):
    for item in ("managed_installs", "managed_uninstalls", "managed_updates", "optional_installs"):
        try:
            for package in manifest[item]:
                if package not in packages_in_manifests:
                    packages_in_manifests.append(package)
        except Exception:
            continue
    try:
        if manifest["conditional_items"]:
            for conditional_item in manifest["conditional_items"]:
                process_manifest(conditional_item, packages_in_manifests)
    except Exception:
        pass


def main():
    munki_repo = get_repo()
    packages_in_repo = []
    requirements_in_repo = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(munki_repo, "pkgsinfo")):
        for dirname in dirnames:
            # Skip directories that start with a period (e.g. ".git")
            if dirname.startswith("."):
                dirnames.remove(dirname)
        for filename in filenames:
            # Skip files that start with a period (e.g. ".DS_Store")
            if filename.startswith("."):
                continue
            filepath = os.path.join(dirpath, filename)
            try:
                pkginfo = plistlib.readPlist(filepath)
                try:
                    if pkginfo["name"] not in packages_in_repo:
                        if "update_for" not in pkginfo:
                            if "installer_type" not in pkginfo:
                                packages_in_repo.append(pkginfo["name"])
                            elif pkginfo["installer_type"] != "apple_update_metadata":
                                packages_in_repo.append(pkginfo["name"])
                    if "requires" in pkginfo:
                        for requirement in pkginfo["requires"]:
                            if requirement not in requirements_in_repo:
                                requirements_in_repo.append(requirement)
                except KeyError:
                    continue
            except ExpatError:
                print >> sys.stderr, "Could not parse %s" % os.path.join(
                    dirpath, filename)

    packages_in_manifests = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(munki_repo, "manifests")):
        for dirname in dirnames:
            # Skip directories that start with a period (e.g. ".git")
            if dirname.startswith("."):
                dirnames.remove(dirname)
        for filename in filenames:
            # Skip files that start with a period (e.g. ".DS_Store")
            if filename.startswith("."):
                continue
            filepath = os.path.join(dirpath, filename)
            try:
                manifest = plistlib.readPlist(filepath)
                process_manifest(manifest, packages_in_manifests)
            except ExpatError:
                print >> sys.stderr, "Could not parse %s" % os.path.join(
                    dirpath, filename)

    unused_packages = list(set(packages_in_repo) - set(requirements_in_repo) - set(packages_in_manifests))
    print "\n    UNUSED PACKAGES:\n"
    pprint(unused_packages)

if __name__ == '__main__':
    main()
