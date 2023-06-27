# Test Organization

## TL;DR: Run the tests

In a container:

```shell
docker compose run --build test
```

Locally:

```shell
# Use "pipenv" to have the right environment
pipenv sync -d
pipenv run pytest

# Get a shell
pipenv shell
```


## Target structure

The target structure for testing shall eventually follow this pattern:

```
└── tests  # top-level tests folder
    ├── README.md  # explains test organization inside this folder
    ├── unit  # name this unit_and_integration if keeping both here
    ├── integration  # optional: omit if kept together with unit tests
    └── e2e
```

### Unit tests

No unit tests are available at the time of writing,
as the container is built from upstream Debian packages
and no source code is kept in this repository.

### Integration tests

Tests which check the *integration* of multiple containers will be grouped into
the folder `integration`.

New tests are written as plain `pytest` based test cases.

### End to end tests

This repository contains no end-to-end tests. *End to end* is understood as
tests against the full running stack, so they are expected to be kept
separately.
