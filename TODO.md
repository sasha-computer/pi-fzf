# pi-fzf TODO

## 1. Rewrite from Go to Python + uv

- [x] Scaffold Python project using domain-search as template
  - `pyproject.toml` with `[project.scripts]` entry point
  - `[tool.uv] package = true`, hatchling build backend
  - `dependency-groups.dev` with pytest, ruff, ty, pre-commit
  - `[tool.ruff]`, `[tool.ty]` config
  - `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `.gitignore`
- [x] Port `main.go` → `pi_fzf/` package
  - `cli.py`, `sessions.py`, `index.py`, `preview.py`, `shell.py`
- [x] Port tests → `tests/` (39 tests, all passing)
- [x] Remove Go files
- [x] `uv tool install .` locally — `pi-fzf` command works
- [ ] Update shell integration (fish config) to point at new binary

## 2. Index assistant messages (Phase 1 — the actual fix)

- [x] Index **both** user and assistant messages — `[YOU]` and `[PI]` tags
- [x] Add **session summary entry** per session — `📋 N msgs · first message...`
- [x] Truncate assistant messages more aggressively (150 chars vs 200 for user)
- [x] Preview pane highlights matched message with `← ← ←`
- [x] Tests cover assistant keyword search (IKKEGOL test case)

## 3. Spin out a Python project template

- [x] Create `~/Developer/template` → pushed to `sasha-computer/template`
  - `pyproject.toml` skeleton with TEMPLATE placeholders
  - `TEMPLATE_PACKAGE/__init__.py`, `TEMPLATE_PACKAGE/cli.py`
  - `tests/__init__.py`, `tests/conftest.py`, `tests/test_cli.py`
  - `.pre-commit-config.yaml` (ruff-check, ruff-format, ty, pytest)
  - `.github/workflows/ci.yml` (4 jobs)
  - `.gitignore`, `LICENSE` (MIT)
- [x] Document the template usage in a README
- [x] Push to GitHub as `sasha-computer/template`
- [x] Update productionize skill to reference the template (done in item 4)

## 4. Update productionize skill

- [x] Changed language/tooling table: Python + uv is now the default, Go only when justified
- [x] Added "Python projects" section referencing `~/Developer/template` (`sasha-computer/template`)
- [x] Added "Tests & CI" checklist section (mandatory for Python projects)
- [x] Updated anti-patterns: tests and CI are now mandatory, removed "don't add tests unless asked"

## 5. Productionize pi-fzf (after rewrite)

- [ ] Hero image
- [ ] Demo recording (VHS)
- [ ] README in productionize format
- [ ] Push to GitHub
- [ ] Update profile README
- [ ] Tweet draft
