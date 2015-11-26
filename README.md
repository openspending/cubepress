# The Cube Press

The cube press is a simple ad-hoc OLAP reporting system that will
consume a [Data Package](http://data.okfn.org/doc/data-package) and
generate a set of pre-defined aggregated reports as static files.

## Installation

The easiest way of using ``cubepress`` is via PyPI:

```bash
$ pip install cubepress
```

Alternatively, check out the repository from GitHub and install it locally:

```bash
$ git clone https://github.com/openspending/cubepress.git
$ cd cubepress
$ pip install -e .
```

## Usage

    cubepress <datapackage.json>

## Testing

    nosetests tests/base.py

## License

``cubepress`` is open source, licensed under a standard MIT license (included in this repository as ``LICENSE``).
