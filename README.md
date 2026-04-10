# The Women in Neuroscience Repository (WiNRepo)

This repository contains the source code for [winrepo.org](https://www.winrepo.org), a platform to increase the visibility of women in neuroscience.

## Quick Start

1. **Fork and clone** the repository.
2. **Create a virtual environment** and install dependencies:
   ```bash
   python3.10 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Set up environment variables** — copy the defaults:
   ```bash
   cp .env.default .env
   ```
4. **Populate the database** with sample data:
   ```bash
   ./tools/refresh_db.sh
   ```
   This creates an SQLite database with test profiles, users, and fixtures. Pre-created accounts:
   - `admin` / `admin` (superuser)
   - `user` / `user` (regular user)
   - `user-profile` / `user` (staff with profile)
5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
   Open [http://localhost:8000/](http://localhost:8000/) in your browser.

### Docker (alternative)

```bash
docker-compose up
```

This starts the Django app with a MySQL database. The app is available at `http://localhost:8000/`.

## Running Tests

```bash
python manage.py test
```

With coverage:
```bash
coverage run --source=profiles manage.py test
coverage report
```

## Important Notes

- Hard-reload your browser (`Ctrl+Shift+R`) to see CSS/JS changes.
- Test responsiveness using your browser's Responsive Design Mode.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Background

This project builds upon work originally developed in the [WiNRepo repository by Gregory Fryns](https://github.com/gregoryfryns/winrepo).
