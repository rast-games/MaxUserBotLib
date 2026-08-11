# Documentation versioning

The documentation starts at **0.8** and uses `mike` to publish multiple MkDocs builds to the `gh-pages` branch. Both English and Russian are built together for every version.

## Preview locally

```bash
uv sync --group dev
uv run mkdocs serve
```

## Publish 0.8

```bash
uv run mike deploy --push --update-aliases 0.8 latest
uv run mike set-default --push latest
```

## Publish a later release

Update documentation together with the source release, then deploy the new minor version while retaining 0.8:

```bash
uv run mike deploy --push --update-aliases 0.9 latest
```

Use major/minor documentation versions unless a patch release changes public behavior. Never edit generated files on `gh-pages` manually; edit `docs/` and deploy again.
