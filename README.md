# HDX Geo Data API

This API provides an interface to query and retrieve humanitarian geographical data from HDX. It provides bindings around [GDAL commands](https://gdal.org/en/stable/programs/index.html#gdal-application) through endpoints matching its syntax.

## Development

### Environment

[uv](https://github.com/astral-sh/uv) is used for package management with development done using Python >=3.13. Pre-commit formatting follows [ruff](https://docs.astral.sh/ruff/) guidelines. To get set up:

```shell
    uv sync
    source .venv/bin/activate
    pre-commit install
```

### Running API

This API can be run natively with the following command:

```shell
uv run task app
```

Alternatively, it can be run with Docker using:

```shell
docker compose up --build
```

## Configuration

### Environment Variables

- `HDX_URL` (required): This determins which HDX site is used to perform authentication and to fetch data from.
- `MIXPANEL_TOKEN` (required for production): enables MixPanel tracking.
- `LOGGING_CONF_FILE` (required for development): By default this is set to `logging.conf`. For development this should be changed to `logging_dev.conf`.
