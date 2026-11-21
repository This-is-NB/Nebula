# Contributing to Nebula

Thanks for helping improve Nebula. Contributions of bug fixes, documentation,
tests, accessibility improvements, and new features are welcome.

## Before you start

- Search existing issues and pull requests to avoid duplicate work.
- For a large change, open an issue first to agree on the approach.
- For security vulnerabilities, follow [SECURITY.md](SECURITY.md) instead of
  opening a public issue.

## Set up the project

Use Python 3.10 or later. From the repository root:

```powershell
python -m pip install -e .
python main.py
```

Or use Pipenv:

```powershell
pipenv install
pipenv run python main.py
```

## Run tests

```powershell
python -m unittest discover -s tests -v
```

Add focused tests for behavior changes. Tests should use temporary directories
for settings and databases rather than real browser data.

## Open a pull request

1. Create a branch from `main`, for example `fix/tab-close-spacing`.
2. Keep the change focused and follow the existing Python style.
3. Run the tests and update documentation when behavior or setup changes.
4. Open a pull request with the problem, solution, and test results.
5. Include screenshots for visible UI changes when practical.

By submitting a contribution, you agree that it may be distributed under the
project's [MIT License](LICENSE).
