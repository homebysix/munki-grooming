# Munki grooming

This is where I'll store a couple scripts that help you tidy up your [Munki](https://www.munki.org/) repository. For now, there's only one:

## show_unused_munki_packages.py

This script attempts to determine which package names are not "used" in your Munki repo. For example, you may have imported something into Munki once (perhaps while testing an AutoPkg recipe) but never added it to any manifests. Therefore, it's just taking up space.

The methodology used by the script is as follows:

1. Iterate through your pkgsinfo folder, collecting all package names.
    - Ignore any packages that are listed as an `update_for`.
    - Ignore any `apple_update_metadata`.
2. While doing the above, also collect any packages listed in `requires`.
3. Collect all package names used in any manifest.
4. Remove the results of #2 and #3 from the total list of packages in #1, and you're left with the unused packages.

Known issues:

- If a package is listed as an `update_for` but the thing it's updating isn't used in a manifest, it will be incorrectly be omitted from the "unused" list.


