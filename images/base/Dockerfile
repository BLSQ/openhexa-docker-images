FROM quay.io/jupyter/scipy-notebook:2026-10-12

LABEL org.opencontainers.image.source=https://github.com/blsq/openhexa-docker-images
LABEL org.opencontainers.image.description="OpenHEXA Jupyter Notebook image with additional tools and libraries"
LABEL org.opencontainers.image.licenses=MIT

USER root

# System libraries
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt-get update && \
  # FUSE Amazon S3
  apt-get install -y s3fs fuse3 libfuse3-dev \
  # Fuse requirements
  gnupg lsb-release

# Install Node.js 22.x
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean

# Quarto CLI (publishing system for .qmd and notebooks). The official .deb is
# self-contained; the conda-forge package needs conda activation scripts that
# these images never run.
# renovate: datasource=github-releases depName=quarto-dev/quarto-cli extractVersion=^v(?<version>.*)$
ARG QUARTO_VERSION=1.10.19
RUN curl -fsSL -o /tmp/quarto.deb "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-$(dpkg --print-architecture).deb" && \
    dpkg -i /tmp/quarto.deb && \
    rm /tmp/quarto.deb

# FUSE Google Cloud Storage
# renovate: datasource=github-releases depName=GoogleCloudPlatform/gcsfuse extractVersion=^v(?<version>.*)$
ARG GCSFUSE_VERSION=3.5.2
RUN gcsFuseRepo=gcsfuse-`lsb_release -c -s` && \
  curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
  gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
  echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt $gcsFuseRepo main" | \
  tee /etc/apt/sources.list.d/gcsfuse.list && \
  apt-get update && \
  apt-get install -y "gcsfuse=${GCSFUSE_VERSION}" && \
  apt-get clean

# FUSE Azure Blob Storage
# The package must match the Ubuntu release of the base image (libfuse3 soname).
# Its architecture suffix is x86_64 on amd64 and arm64 on arm64.
# renovate: datasource=github-releases depName=Azure/azure-storage-fuse extractVersion=^blobfuse2-(?<version>\d+\.\d+\.\d+)$
ARG BLOBFUSE2_VERSION=2.5.6
RUN arch=$(dpkg --print-architecture | sed 's/^amd64$/x86_64/') && \
    deb="blobfuse2-${BLOBFUSE2_VERSION}-Ubuntu-$(lsb_release -r -s).${arch}.deb" && \
    curl -fsSL "https://github.com/Azure/azure-storage-fuse/releases/download/blobfuse2-${BLOBFUSE2_VERSION}/${deb}" -o "/tmp/${deb}" && \
    dpkg -i "/tmp/${deb}" && \
    rm "/tmp/${deb}"


WORKDIR $HOME

# Add locales
RUN locale-gen fr_FR fr_FR.UTF-8 es_ES es_ES.UTF-8 de_DE de_DE.UTF-8 && \
    update-locale

# /home/hexa symlink (preferred path for data pipelines)
RUN ln -s /home/jovyan /home/hexa && \
  chown jovyan /home/hexa

USER ${NB_UID}

RUN mamba install --yes  -c conda-forge -c blsqtech  \
  # This package is included in other libraries and one (don't know which one) is requesting the version '*.*'.
  # This is not compatible with the libmamba resolver of Conda and make next conda install to fail.
  'blas=2.131' \
  'fsspec>=2025,<2026' \
  'gcsfs>=2025,<2026' \
  'papermill>=2.6,<2.7' \
  'psycopg2-binary=2.*' \
  'duckdb>=1.3,<1.5' \
  # Install openhexa-sdk & openhexa-toolbox from anaconda \
  'bioconda::epiweeks' \
  'openhexa.sdk=2.22.6' \
  'openhexa.toolbox=2.11.3' \
  # Jupyter extensions
  'jupyter-resource-usage' \
  'jupyterlab_code_formatter' \
  # jupytext opens and pairs Quarto .qmd files as notebooks (uses the Quarto CLI above).
  # Its frontend bundle is built against a specific JupyterLab minor (1.19.5+
  # needs 4.6); if .qmd files stop opening as notebooks after a base image
  # bump, check the browser console for "Failed to create module".
  'jupytext>=1.19,<1.20' && \
  mamba clean --all -f -y && \
  fix-permissions "${CONDA_DIR}"

# jupyterlab-quarto renders Quarto markdown (callouts, cross-references...) in
# notebook cells. Only published on PyPI; it has no Python dependencies.
RUN pip install --no-cache-dir 'jupyterlab-quarto>=0.3,<0.4' && \
  fix-permissions "${CONDA_DIR}"

RUN jupyter labextension disable "@jupyterlab/apputils-extension:announcements"

# custom config
COPY jupyter_notebook_config.py /etc/jupyter/
COPY --chown=${NB_UID}:${NB_UID} files/overrides.json /opt/conda/share/jupyter/lab/settings/

ENV HEXA_ENVIRONMENT=CLOUD_JUPYTER


# s3f fuse
COPY files/scripts/fuse.conf /etc/.
# k8s: same as sample files, we need to copy those to a temp location
COPY files/scripts/* /tmp/hexa_scripts/
# Please note that if a PVC is mounted at /home/jovyan (for OpenHEXA legacy notebooks), this directory will be
# "lost" - they need to be copied again from /tmp after mounting the PVC
COPY files/scripts/* /home/jovyan/.hexa_scripts/
# sample files
COPY files/sample_files/* /home/jovyan

# Copy the entrypoint at the same location as the ones defined in the base image
COPY entrypoint.sh /usr/local/bin/

# Set PYTHONUNBUFFERED to ensure that Python output is sent straight to terminal
ENV PYTHONUNBUFFERED=1
# Tell PROJ where its database is. Without it, GDAL logs "ERROR 1: PROJ:
# proj_create_from_database: Open of /opt/conda/share/proj failed" on every
# `import fiona`, and R's sf (blsq, blsq-r) sees every CRS as missing.
# PROJ_LIB is the older name of PROJ_DATA; set both for tools reading either.
ENV PROJ_DATA=/opt/conda/share/proj \
    PROJ_LIB=/opt/conda/share/proj

# Redefine the entrypoint to be able to launch pipelines as well
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD singleuser
