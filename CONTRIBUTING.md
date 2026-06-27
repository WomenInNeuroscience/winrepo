# Contributing to WiNRepo

Thank you for your interest in contributing! This guide covers the development
workflow. For first-time setup (virtualenv, database, running the server), see
the **Quick Start** in [README.md](README.md).

## TL;DR

```bash
git checkout -b my-change          # branch off main
python manage.py test              # confirm green before you start
# ... make your change, add tests ...
python manage.py test              # confirm green before you push
git commit -m "fix(profiles): ..." # conventional commit message
# open a PR against main
```

## Getting Started

1. Fork the repository and clone your fork.
2. Follow the **Quick Start** in [README.md](README.md) to get a running dev
   environment (Python 3.10, `.venv`, `cp .env.default .env`,
   `./tools/refresh_db.sh`, `python manage.py runserver`).
3. Create a branch from `main` for your changes.

The default `.env.default` is safe for local work out of the box: it uses
SQLite, prints emails to the console, and uses Google's always-pass reCAPTCHA
test keys. You do **not** need any real credentials to develop locally.

## Development Workflow

1. **Start from green.** Run `python manage.py test` before you change anything,
   so you know any later failure is yours.
2. **Test before you touch.** If you're changing existing behaviour, first add a
   test that captures the *current* behaviour, watch it pass, then make your
   change. This is how we keep regressions out of a 5-year-old codebase.
3. **Write tests for new features and bug fixes.** Put them in
   `profiles/tests/` next to the related `test_*.py` file.
4. **Keep commits focused** — one logical change per commit.
5. **Run tests again before submitting** your PR:
   ```bash
   python manage.py test
   ```
   For coverage:
   ```bash
   coverage run --source=profiles manage.py test && coverage report
   ```

## Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): short summary in the imperative mood

Optional body explaining the what and why.
```

Common types in this repo: `feat`, `fix`, `refactor`, `test`, `docs`, `style`,
`chore`, `ci`, `build`. Scope is the area touched, e.g. `fix(signup): ...`,
`feat(profiles): ...`, `ci(deploy): ...`.

## Pull Requests

- Link your PR to any related issues (e.g., "Closes #42").
- Provide a clear description of what changed and why.
- Make sure CI is green — pushes run the test suite automatically.
- Don't include unrelated changes in the same PR.

A push to `main` triggers the deploy workflow (tests, then deploy to
PythonAnywhere), so `main` must always stay green.

## Coding Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code.
- Use clear, descriptive names for variables, functions, and arguments.
- Keep templates and JS consistent with existing patterns.

## Project Map

A quick orientation — most work happens in the `profiles` app:

| Path | What's there |
|------|--------------|
| `profiles/models.py` | Core data models (Profile, Recommendation, Publication, Country, User) |
| `profiles/views.py` | Page and form views, including sign-up and profile flows |
| `profiles/forms.py` | Django forms and validation (incl. honeypot / disposable-email checks) |
| `profiles/emails.py` | Email message builders |
| `profiles/templates/` | HTML templates |
| `profiles/static/` | CSS and JS |
| `profiles/tests/` | Test suite (`test_*.py`) |
| `winrepo/settings.py` | Project settings (reads from `.env`) |
| `tools/` | Helper scripts (see below) |

## Helper Scripts

| Script | Purpose |
|--------|---------|
| `tools/refresh_db.sh` | (Re)create the local SQLite dev database with sample fixtures |
| `tools/backup_db.sh` | Back up the database (used in production) |
| `tools/refresh_env.sh` | Production deploy script (pull, migrate, collectstatic, restart) |

## Common Tasks

```bash
# Reset your local database to a clean state with sample data
./tools/refresh_db.sh

# Create an admin user (if you didn't use the seeded `admin`/`admin`)
python manage.py createsuperuser

# Run a single test module
python manage.py test profiles.tests.test_signup
```

> **Note on profiles vs. users:** historically some profiles exist without an
> associated user account. When working on anything that links profiles and
> users, don't assume a one-to-one mapping — handle the "profile with no user"
> case explicitly.

## Reporting Issues

To report a bug or suggest a feature,
[open an issue](https://github.com/WomenInNeuroscience/winrepo/issues/new).
Please include steps to reproduce for bugs.
