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

    cubepress -p <datapackage> <aggregates.json>

where `aggregates.json` is specified as a JSON list of aggregates
written in plain SQL:

    [{
      "sql": "SELECT admin, SUM(executed) as amount FROM 'table' WHERE year = 2006 GROUP BY admin",
      "file": "by-department",
      "format": "csv"
    }]

Cubepress can also generate aggregates from specially written report [YAML files](https://github.com/openspending/cubepress/blob/master/tests/fixtures/awards.yaml).

## Testing

    nosetests tests/base.py

## License

``cubepress`` is open source, licensed under a standard MIT license (included in this repository as ``LICENSE``).
