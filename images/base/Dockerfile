FROM quay.io/jupyter/scipy-notebook:2025-03-23

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

# FUSE Google Cloud Storage
RUN gcsFuseRepo=gcsfuse-`lsb_release -c -s` && \
  echo "deb https://packages.cloud.google.com/apt $gcsFuseRepo main" | \
  tee /etc/apt/sources.list.d/gcsfuse.list && \
  curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
  apt-key add - && \
  apt-get update && \
  apt-get install -y gcsfuse && \
  apt-get clean

# FUSE Azure Blob Storage


RUN curl -L https://github.com/Azure/azure-storage-fuse/releases/download/blobfuse2-2.5.0-preview.1/blobfuse2-2.5.0.preview.1-Ubuntu-22.04.x86_64.deb -o blobfuse2-2.5.0.preview.1-Ubuntu-22.04.x86_64.deb && \
    dpkg -i blobfuse2-2.5.0.preview.1-Ubuntu-22.04.x86_64.deb && \
    rm blobfuse2-2.5.0.preview.1-Ubuntu-22.04.x86_64.deb


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
  'openhexa.sdk=2.15.2' \
  'openhexa.toolbox=2.8.1' \
  # Jupyter extensions
  'jupyter-resource-usage' \
  'jupyterlab_code_formatter' && \
  conda clean --all -f -y && \
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

# Redefine the entrypoint to be able to launch pipelines as well
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD singleuser
