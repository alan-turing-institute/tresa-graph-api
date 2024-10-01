# tresa-graph-api

[![Actions Status][actions-badge]][actions-link]
[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

A command line interface for the Trusted Research Environment Service Area (TRE SA) to check the users and groups in the Alan Turing Institute's Data Safe Haven (DSH) using the Microsoft Graph API.

## Installation

<!-- ```bash
python -m pip install tresa_graph_api
``` -->

From source:

```bash
git clone https://github.com/alan-turing-institute/tresa-graph-api
cd tresa-graph-api
```

Then install the package:

```bash
python -m pip install .
```

or in editable mode (useful for development):

```bash
python -m pip install -e .
```

## Usage

This tool is under development. It currently only prints the outputs of the queries to the terminal.

See the CLI help by running:

```bash
python -m tresa_graph_api.shm_users_groups -h
```

The tool has two positional arguments: `user` and `group`.

See the help for the `user` subcommand by running:

```bash
python -m tresa_graph_api.shm_users_groups user -h
```

See the help for the `group` subcommand by running:

```bash
python -m tresa_graph_api.shm_users_groups group -h
```

### Example

Get information for user named Harry Potter:

```bash
python -m tresa_graph_api.shm_users_groups user --name "Harry Potter"
```

Get information for group named Sandbox:

```bash
python -m tresa_graph_api.shm_users_groups group --name sandbox
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for instructions on how to contribute.

## License

Distributed under the terms of the [MIT license](LICENSE).


<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/alan-turing-institute/tresa-graph-api/workflows/CI/badge.svg
[actions-link]:             https://github.com/alan-turing-institute/tresa-graph-api/actions
[pypi-link]:                https://pypi.org/project/tresa-graph-api/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/tresa-graph-api
[pypi-version]:             https://img.shields.io/pypi/v/tresa-graph-api
<!-- prettier-ignore-end -->
