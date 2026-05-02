# Contributing to Kailash

This document describes the workflow, conventions, and tooling expectations
for contributors.

## Branching Model

- `main` — always deployable. Protected.
- `feat/<short-description>` — new features.
- `fix/<short-description>` — bug fixes.
- `chore/<short-description>` — tooling, docs, refactors without behavior change.
- `hotfix/<short-description>` — urgent production patches.

## Commit Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

[optional body]
[optional footer]
```

Common types: `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `build`, `ci`,
`chore`. Scope should reference the affected module (e.g. `backend`, `frontend`,
`deploy`, `agents/ganesha`).

Examples:
- `feat(backend): add rate limiter to /auth/login`
- `fix(frontend): correct KPI widget rounding`
- `docs(deployment): clarify MongoDB Atlas setup`

## Pull Requests

1. Open a PR against `main`.
2. Link the tracking issue if one exists.
3. Ensure the PR title follows Conventional Commits.
4. Ensure tests pass: `make test` and `cd frontend && yarn build`.
5. Request at least one reviewer from the code owners.
6. Squash-merge once approved and CI is green.

## Local Tooling

### Python (backend, tests)

- Python 3.11+
- `pip install -r backend/requirements.txt`
- Run tests: `make test`

### JavaScript (frontend)

- Node.js 18+, Yarn 1.x
- `cd frontend && yarn install`
- Build: `yarn build`

### Pre-flight checklist before pushing

- [ ] Code compiles / lints clean (`make lint`)
- [ ] Tests added or updated
- [ ] Docs updated if behavior changed
- [ ] No secrets or credentials committed
- [ ] Frontend builds cleanly

## Security

Never commit secrets, private keys, `.env` files, or production credentials.
Use environment variables and the deployment secret store. If you discover a
vulnerability, email `security@kailash-ai.in` — do not open a public issue.

## Code Style

- **Python**: PEP 8, type hints where practical. Ruff enforces formatting.
- **JavaScript/React**: functional components, hooks, Prettier defaults.
- **Markdown**: one sentence per line is preferred for diff readability.

## Release

1. Update `CHANGELOG.md` under `## [Unreleased]`.
2. Bump versions in `backend/app/__init__.py` and `frontend/package.json`.
3. Tag: `git tag -a vX.Y.Z -m "release: vX.Y.Z"`.
4. Push tags: `git push --tags`.
