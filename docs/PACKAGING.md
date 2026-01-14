# Packaging Guide for PySchemaElectrical using `uv`

This guide explains how to build the project into a distribution package and upload it to PyPI using `uv`.

## Prerequisites

- **uv**: Ensure `uv` is installed (`uv --version`).
- **PyPI Account**: You need an account on [PyPI](https://pypi.org/).
- **API Token**: Generate an API token from your PyPI account settings.

## 1. Verify Project Configuration

Your `pyproject.toml` is already configured for building with `setuptools`.

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "pyschemaelectrical"
version = "0.1.2"
# ... other metadata ...
```

**Action**: Before every release, remember to bump the `version` in `pyproject.toml`.

## 2. Build the Package

`uv` provides a fast build command that creates the source distribution (`.tar.gz`) and wheel (`.whl`).

Run the following command in the project root:

```bash
uv build
```

This will create a `dist/` directory containing:
- `pyschemaelectrical-0.1.2.tar.gz`
- `pyschemaelectrical-0.1.2-py3-none-any.whl`

## 3. Publish to PyPI

`uv` also supports publishing directly to PyPI.

### Option A: Publish using `uv` (Recommended)

1.  **Configure API Token**:
    You can provide the token via the `UV_PUBLISH_TOKEN` environment variable or the `--token` flag.

    ```bash
    # Setting environment variable (Windows PowerShell)
    $env:UV_PUBLISH_TOKEN = "pypi-AgEIpy..."
    ```

2.  **Run Publish Command**:

    ```bash
    uv publish
    ```

    By default, this looks for files in `dist/` and uploads them to real PyPI.


## Summary Checklist

- [ ] Update `version = "x.y.z"` in `pyproject.toml`
- [ ] Run `uv build`
- [ ] Inspect contents of `dist/` (optional verification)
- [ ] Run `uv publish` (with token)
