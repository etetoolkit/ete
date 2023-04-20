# Contributing to ETE

## Pull requests and development workflow

Official versioned releases are done via conda and pypi. However, the
default branch at GitHub is also expected to be stable and receives
more frequent additions and fixes.

We try to have new development in feature-specific branches or
forks. We merge pull requests after reviewing changes and confirming
that all tests are passed.

We ask for new contributions to include their own tests that checks
the correct behavior of the new code.

If you start working on a new feature or a fix, please consider
letting others know (by opening or updating GitHub issues for
example).


## Bug reporting and feature requests

The preferred way to report a problem or request/disccuss new features
is by opening a new issue at https://github.com/etetoolkit/ete/issues
. Please check if there is already such an open issue before creating
a new one.


## Running tests

To run the tests, after you have a local installation (see
[README.md](README.md) for details), you can:

```sh
python -m unittest tests.test_arraytable
python -m unittest tests.test_clustertree
python -m unittest tests.test_gtdbquery
python -m unittest tests.test_interop
python -m unittest tests.test_phylotree
python -m unittest tests.test_seqgroup
python -m unittest tests.test_tree
python -m unittest tests.test_treediff
python -m unittest tests.test_orthologs_group_delineation
python -m unittest tests.test_ncbiquery
python -m unittest tests.test_nexus
```

Eventually we will fix the remaining tests, and then we expect to run them all with:

```sh
python -m unittest tests.test_all
```
