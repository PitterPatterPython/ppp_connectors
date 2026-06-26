# pyapiary — Claude Code Guidelines

**No change is merged without the project owner's review and approval**
Contributors open PRs against `develop`; never push directly to `main`.

---

## Project layout

```
src/pyapiary/
  api_connectors/       # HTTP API connectors (Broker subclasses)
  dbms_connectors/      # Database connectors
  helpers.py            # Shared utilities — edit with care
  tests/
    test_<name>/
      test_unit_<name>.py
      test_unit_async_<name>.py
      test_integration_<name>.py
      cassettes/        # VCR cassettes for integration tests
dev_env/                # Local scratch scripts — never imported by the package
```

Do not create files outside this structure without an explicit request.

---

## Dependencies — do not touch without being asked

- **Never add a package** to `pyproject.toml` or `uv.lock`/`poetry.lock` unless the contributor's task explicitly requires a new dependency and the maintainer has approved it.
- **Never remove a package** from `pyproject.toml` even if it appears unused in the files you're editing. Removals require explicit sign-off.
- Package management uses **Poetry**. Run `poetry install --all-extras` to sync; do not use `pip install` directly.

---

## Connector patterns

Every connector follows the same structure. Study an existing one (e.g.,
`flashpoint.py`) before writing a new one.

### API connectors (`api_connectors/`)

- Sync class inherits from `Broker`; async class inherits from `AsyncBroker`.
- Decorate every public method with `@log_method_call`.
- Pull credentials from the constructor arg first, then `self.env_config.get("KEY")`.
- Raise `ValueError` with the env var name when a required credential is missing.
- Name the file after the service in lowercase (e.g., `acme.py`).

### DBMS connectors (`dbms_connectors/`)

- Follow the same sync/async pairing and credential pattern.
- Provide both a sync and async class in the same file when the service
  supports it (see `mongo.py` / `mongo_async.py` for the split-file variant).

---

## Tests — required for every change

All new public methods and new connectors must ship with tests. No exceptions.

### Structure

Each connector gets its own subdirectory under `src/pyapiary/tests/`:

```
tests/test_<name>/
  test_unit_<name>.py          # sync class, mocked with unittest.mock
  test_unit_async_<name>.py    # async class, mocked with AsyncMock + @pytest.mark.asyncio
  test_integration_<name>.py   # real HTTP via VCR cassette
  cassettes/                   # .yaml cassette files recorded once, committed
```

### What each test file must cover

**Unit (sync & async):**
- `__init__` with explicit credential arg
- `__init__` picking up credential from env var (`@patch.dict("os.environ", ...)`)
- `__init__` raising `ValueError` when credential is absent
- One test per public method, mocking the underlying HTTP call

**Integration:**
- At least one method per connector exercised against a recorded VCR cassette.
- Cassette files are committed. Never record against a live API in CI.

### Running tests

```bash
poetry run pytest --ignore=dev_env
```

CI runs this exact command. All tests must pass before opening a PR.

---

## What not to do

- Do not add abstractions, base classes, or helpers that have only one
  consumer. Put the logic in the connector.
- Do not add comments that restate what the code does. A short docstring on a
  class or method is fine; inline narrative comments are not.
- Do not introduce new test frameworks, fixtures libraries, or pytest plugins.
  The existing stack is `pytest`, `pytest-mock`, `pytest-asyncio`, and `vcrpy`.
- Do not touch `ci.yml` or `release.yml` without explicit instruction.
- Do not modify `helpers.py` as a side effect of connector work.
- Do not leave `dev_env/` scripts in a broken state; that directory is for
  local experimentation only and is ignored by CI.

---

## PR checklist

Before opening a PR, verify:

- [ ] `poetry run pytest --ignore=dev_env` passes locally
- [ ] New connector or method has all three test files (unit sync, unit async, integration)
- [ ] No packages added or removed from `pyproject.toml`
- [ ] No files created outside the established directory structure
- [ ] PR targets `develop`, not `main`
