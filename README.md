# openhexa-docker-images

A repository of Docker images for OpenHexa workspaces (notebooks and pipelines)

## Building locally

```bash
docker build -t openhexa-base-environment images/base
docker build -t openhexa-blsq-environment --build-arg BASE_IMAGE=openhexa-base-environment images/blsq
docker build -t openhexa-blsq-r-environment --build-arg BASE_IMAGE=openhexa-base-environment images/blsq-r
```

## Image tags

| Tag                | When updated                       |
| ------------------ | ---------------------------------- |
| `:latest`          | Official releases only             |
| `:latest-unstable` | Every push to main                 |
| `:main`            | Every push to main                 |
| `:vX.Y.Z`          | Official releases (version number) |

## Quarto

The base image includes the [Quarto](https://quarto.org) CLI, `jupytext` and
the `jupyterlab-quarto` extension:

- `.qmd` files open as notebooks in JupyterLab (double-click, or *Open With →
  Notebook*); `jupytext` keeps the `.qmd` file as the source of truth. The
  launcher and *File → New* also offer a *Quarto Notebook*.
- `jupyterlab-quarto` renders Quarto markdown (callouts, cross-references,
  figure options...) in notebook cells.
- `quarto render` works from a terminal or a pipeline.

The jupytext frontend is built against a specific JupyterLab minor version. If
`.qmd` files open in the text editor after a base image bump, look for
`Failed to create module: package: jupyterlab-jupytext` in the browser console.
