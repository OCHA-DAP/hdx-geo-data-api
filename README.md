# HDX Geo Data API

This API provides an interface to query and retrieve humanitarian geographical data from HDX. It provides bindings around [GDAL commands](https://gdal.org/en/stable/programs/index.html#gdal-application) through endpoints matching its syntax.

## Development

### Environment

Development is currently done using Python 3.13. We recommend using uv to create a virtual environment and install all packages:

```shell
    uv sync && source .venv/bin/activate
```

### Pre-commit

Be sure to install `pre-commit`, which is run every time you make a git commit. With pre-commit, all code is formatted according to [ruff](https://docs.astral.sh/ruff/) guidelines.

```shell
    uv run pre-commit install
```

### Running

This API can be run natively with the following command:

```shell
uv run task app
```

Alternatively, it can be run with Docker using:

```shell
docker compose up --build
```
