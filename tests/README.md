# a-plus-rst-tools/tests

This directory contains Python unit tests for A-plus RST tools.
The tests also serve as documentation on how parts of the software should
operate.

## Prerequisites

As the unit tests are run outside the Docker container apluslms/compile-rst,
you will need:

- [Python 3](https://www.python.org)
- [Sphinx](https://www.sphinx-doc.org/)
- [Testfixtures](https://testfixtures.readthedocs.io/en/latest/index.html)

Sphinx and Testfixtures can be installes as a Python packages, e.g.

```
pip3 install sphinx testfixtures
```

See the [top level README](../README.md) for details.

## Running the tests

`python3 -m unittest` runs all the unit tests.
