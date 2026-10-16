---
title: Contributing
description: Contribute to BinomoAPI, the open-source Binomo Python library. Set up a dev environment, follow the code style, preview the docs and send a pull request.
nav_order: 12
---

# Contributing to BinomoAPI
{: .no_toc }

BinomoAPI is community-maintained, and every fix, new asset, example or docs improvement helps other traders. Thank you for being here. 💛
{: .fs-5 .fw-300 }

1. TOC
{:toc}

---

## Ways to help

- ⭐ **Star the repo.** It's the easiest way to help others find the project.
- 🐛 **Report bugs** with a minimal script and the redacted error output: [open an issue](https://github.com/ChipaDevTeam/BinomoAPI/issues/new).
- 📈 **Update assets.** Binomo changes its asset list over time; edit [`BinomoAPI/assets.json`](https://github.com/ChipaDevTeam/BinomoAPI/blob/main/BinomoAPI/assets.json).
- 🧪 **Add examples** to [`examples/`](https://github.com/ChipaDevTeam/BinomoAPI/tree/main/examples).
- 📝 **Improve these docs.** Every page has an "Edit this page on GitHub" link at the bottom.
- 💬 **Answer questions** in [Discord](https://discord.gg/p7YyFqSmAz).

Good first contributions: a public trade-result API, retry/reconnect helpers, and unit tests for the models and the asset helpers.

## Development setup

```bash
git clone https://github.com/<your-username>/BinomoAPI.git
cd BinomoAPI
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -e .
pip install -r requirements-dev.txt
```

## Before you open a pull request

CI runs these checks on Python 3.8–3.11. Run them locally first:

```bash
black BinomoAPI                      # format
flake8 BinomoAPI --select=E9,F63,F7,F82
mypy BinomoAPI --ignore-missing-imports
python -m build && twine check dist/*
```

{: .warning }
> Never commit credentials, auth tokens or `.env` files. Scripts that hit the real Binomo API must read credentials from environment variables.

## Pull request flow

1. Fork the repo and create a branch: `git checkout -b fix/short-description`.
2. Make your change, and update the docs if behaviour changes.
3. Run the checks above.
4. Open a PR against `main` that describes **what** changed and **why**.

## Previewing the docs

The documentation site is built by GitHub Pages from the [`docs/`](https://github.com/ChipaDevTeam/BinomoAPI/tree/main/docs) folder using the [Just the Docs](https://just-the-docs.com) theme. To preview it locally with Docker:

```bash
docker run --rm -it -p 4000:4000 -v "$PWD/docs:/site" -w /site ruby:3.1 \
  sh -c "gem install github-pages --no-document && jekyll serve --host 0.0.0.0"
```

Then open <http://localhost:4000/BinomoAPI/>.

To add a page, create `docs/your-page.md` with front matter that sets `title`, a search-friendly `description` and `nav_order`.

## Code of conduct

Be kind, assume good intent and help newcomers. Harassment or spam gets you removed from the project and community.
