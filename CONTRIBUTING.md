# Contributing

Thanks for your interest in ResQPulse AI. Issues and pull requests are welcome.

## Getting set up
Follow the **Quick start** in the [README](README.md). You can work on the dashboard and the API without any model
weights by starting the backend with `make api-fake`.

## Workflow
1. Open an issue first for anything larger than a small fix, so the approach can be agreed.
2. Create a branch from `main`: `feat/<short-name>`, `fix/<short-name>` or `docs/<short-name>`.
3. Keep each pull request to one change. Describe what changed, why, and how you tested it.
4. Run the tests before pushing: `make test`. Add a test for any bug you fix.
5. Add a short entry to [docs/UPDATE.md](docs/UPDATE.md) (newest first).

## Conventions
- Python 3.10+, standard library first, then third-party, then local imports.
- Data formats and the API contract live in [docs/SCHEMA.md](docs/SCHEMA.md); change the schema there first.
- Never commit model weights, raw third-party data, tweet text, `.env` files or certificates. `.gitignore` covers these.
- Report scores only from `scripts/evaluate.py`, on held-out data, next to the baseline.

## Code of conduct
This project follows the [Code of Conduct](CODE_OF_CONDUCT.md).
