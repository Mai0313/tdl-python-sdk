# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`tdl-python-sdk` is a thin Python wrapper around the external [`tdl`](https://github.com/iyear/tdl) CLI binary. It does not re-implement Telegram protocol logic — every public method spawns a `tdl` subprocess. Pydantic models validate inputs and serialize themselves into CLI flags; the runner captures stdout/stderr/return code and raises typed exceptions.

The `tdl` binary must be installed separately and on `PATH` (or pass `tdl_path=` to the client). Tests mock `subprocess.run`, so the binary is not needed for the test suite.

## Common Commands

All development tasks go through `uv` (managed in `pyproject.toml`).

```bash
make fmt                       # uv run pre-commit run -a  (ruff, mypy, codespell, mdformat, gitleaks, etc.)
make test                      # uv run pytest             (xdist parallel, doctest-modules, 80% coverage floor)
make gen-docs                  # Regenerate MkDocs sources under docs/ (gitignored)
make clean                     # Wipe caches, reports, generated docs
make uv-install                # Bootstrap uv itself on a new machine

uv sync --all-groups           # Install runtime + dev + test + docs deps
uv run pre-commit install      # Install git hooks (pre-commit + post-checkout/merge/rewrite)

uv run pytest tests/test_models.py            # Single file
uv run pytest -k "download"                   # Filter by keyword
uv run pytest tests/test_client.py::TestLogin # Single class
uv run pytest --no-cov                        # Skip the 80% coverage gate when iterating
```

`pytest` runs with `--doctest-modules` against `src/`, so docstring examples in `src/tdl_sdk/*.py` are executed as tests. Keep code blocks in docstrings runnable, or wrap them so `pytest` does not try to execute them.

Coverage configuration writes XML/JUnit/HTML to `.github/reports/` and `.github/coverage_html_report/`. CI uses these paths.

## Architecture

The package is intentionally small (five modules under `src/tdl_sdk/`). The non-obvious wiring is the **CLI flag serialization pipeline**, which is what most new features touch.

### Data flow for a single command

```
TDL.<method>(Options(...))
        │
        ▼
TDL.runner  (computed_field → TDLRunner(tdl_path, global_options))
        │
        ▼
TDLRunner.run(command, options, positional_args, timeout)
        │
        ├─ [tdl_path] + global_options.cli_args  ← prefix
        ├─ command                              ← e.g. ["chat", "ls"]
        ├─ options.cli_args                     ← flags from Pydantic model
        └─ positional_args                      ← e.g. extension name
        │
        ▼
subprocess.run(cmd, capture_output=True, timeout=timeout)
        │
        ├─ FileNotFoundError      → TDLNotFoundError
        ├─ TimeoutExpired         → TDLTimeoutError
        ├─ returncode != 0        → TDLCommandError(stdout, stderr, return_code)
        └─ success                → TDLResult(stdout, stderr, return_code)
```

### CLI flag serialization rules (`_models.py`)

`_BaseOptions.cli_args` walks `model_fields`. For each field:

- `None` → skipped.
- `False` (bool) → skipped (so default `False` flags do not appear).
- `True` (bool) → emit `--flag` alone, no value.
- `list` → emit `--flag <item>` once per item (used for repeatable flags like `--url`, `--include`).
- `dict` → emit `--flag k1=v1,k2=v2` (used for `--storage`, `--to`).
- `Enum` → emit the enum's string value.
- Anything else → emit `--flag <str(value)>`.

The flag name is `field_info.alias or field_name`. Use a Pydantic `alias=` whenever the CLI flag differs from a valid Python attribute name — Python keywords (`continue`, `from`), hyphenated flags (`dry-run`, `skip-same`, `rewrite-ext`), or renames (`type`, `filter`, `input`, `all`, `dir`).

`GlobalOptions` is the exception: it has its own `cli_args` that suppresses fields equal to the `tdl` defaults (`limit=2`, `ns="default"`, `pool=8`, `reconnect_timeout="5m"`, `threads=4`). Adding a new global option requires updating that `flag_map` — `_BaseOptions` is not used here.

### Adding a new command

1. Define `XxxOptions(_BaseOptions)` in `_models.py`. Use `alias=` for any CLI flag that is a Python keyword, hyphenated, or differs in spelling from the attribute.
2. Add the method to `TDL` in `_client.py`. Call `self.runner.run(["xxx"], options or XxxOptions(), timeout=self.timeout)`. Use `positional_args=[name]` for commands that take a non-flag argument (see `ext_install`, `ext_remove`, `ext_upgrade`).
3. Export the new model from `src/tdl_sdk/__init__.py` (alphabetically inside the existing tuple).
4. Add coverage in `tests/test_models.py` (serialization), `tests/test_client.py` (correct subcommand + option type passed to runner), and `tests/test_runner.py` if subprocess argv ordering needs to be verified. The 80% coverage gate is enforced by `pytest`.

### Exception hierarchy

All exceptions inherit from `TDLError`, which carries `stdout`, `stderr`, and `return_code` attributes. Subclasses are `TDLNotFoundError` (binary missing), `TDLCommandError` (non-zero exit), `TDLTimeoutError` (subprocess timeout), and `TDLParseError` (currently unused — reserved for future JSON parsing). Do not swallow command failures by catching at the runner; let them propagate so callers can inspect `e.stderr` / `e.return_code`.

## Repository Conventions

- **No CLI entrypoint exists yet.** `pyproject.toml` advertises `[project.scripts] cli = "tdl_sdk.cli:main"` and `tdl_sdk = "tdl_sdk.cli:main"`, plus `[tool.poe.tasks]` that point at `src/tdl_sdk/cli.py`, but `src/tdl_sdk/cli.py` does not exist. Do not promise console commands in docs until that file is implemented or the manifest is corrected. Same applies to `build_release.yml`, which expects an executable build artifact that cannot currently be produced.
- **Commit messages and PR titles must be English** and follow Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, …). The Semantic Pull Request workflow enforces this.
- Branches follow `feat/`, `fix/`, `docs/`, `chore/` prefixes. The Tests workflow skips PRs whose branch starts with `chore/`, `ci/`, or `docs/`.
- README has three mirrored versions: `README.md` (canonical English), `README.zh-TW.md`, `README.zh-CN.md`. Keep them in sync when editing user-facing docs. Badges and code blocks must be preserved across translations.
- `docs/` is generated by `make gen-docs` and is gitignored — never edit it directly.
- Coverage threshold is 80% (`--cov-fail-under=80` in `pyproject.toml`); tests run on Python 3.11, 3.12, and 3.13 in CI.
- Use `rg` instead of `grep` for searches in this repo.
- When fixing bugs, locate the root cause; do not paper over by catching and ignoring errors at the runner boundary.
