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
