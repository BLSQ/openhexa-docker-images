FROM quay.io/jupyter/datascience-notebook:2025-01-06

LABEL org.opencontainers.image.source=https://github.com/blsq/openhexa-docker-images
LABEL org.opencontainers.image.description="OpenHEXA Jupyter Notebook image with additional tools and libraries"
LABEL org.opencontainers.image.licenses=MIT

USER root


# System libraries
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt-get update && \ 
  # FUSE Amazon S3 
  apt-get install -y s3fs \
  # ICU (for R)
  libicu-dev \
  # XML R library dependencies
  libcurl4-openssl-dev libxml2-dev \
  # Fuse requirements
  gnupg lsb-release

# FUSE Google Cloud Storage
RUN gcsFuseRepo=gcsfuse-`lsb_release -c -s` && \
  echo "deb https://packages.cloud.google.com/apt $gcsFuseRepo main" | \
  tee /etc/apt/sources.list.d/gcsfuse.list && \
  curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
  apt-key add - && \
  apt-get update && \
  apt-get install -y gcsfuse && \
  apt-get clean

WORKDIR $HOME

# Add locales
RUN locale-gen fr_FR fr_FR.UTF-8 es_ES es_ES.UTF-8 de_DE de_DE.UTF-8 && \
    update-locale

# /home/hexa symlink (preferred path for data pipelines)
RUN ln -s /home/jovyan /home/hexa
RUN chown jovyan /home/hexa
RUN chown -R jovyan /opt/conda


USER ${NB_UID}

# Set environment variable for Conda cache directory inside the container
ENV CONDA_PKGS_DIRS=/opt/conda/pkgs

RUN conda uninstall r-base && conda install --yes  -c conda-forge -c R -c blsqtech -c bioconda \
  'r-base=4.4.*' \
  'r-irkernel=1.3.*' \
  'nodejs=22.12.*' \
  'fsspec=2023.12.2' \
  'gcsfs=2023.12.2' \
  'papermill=2.6.*' \
  # Install openhexa-sdk & openhexa-toolbox from anaconda
  'openhexa.sdk=1.*' \
  'openhexa.toolbox=1.4.*' \
  # Jupyter extensions
  'jupyterlab-git=0.*' \
  'jupyter-resource-usage=1.*' \
  'jupyterlab_code_formatter=2.*' && \
  conda clean --all -y


RUN jupyter labextension disable "@jupyterlab/apputils-extension:announcements"
# Build Jupyterlab - needed for extensions
RUN jupyter lab build -y --dev-build=False && \
  jupyter lab clean -y && \
  npm cache clean --force && \
  rm -rf "/home/${NB_USER}/.cache/yarn"

# custom config
COPY jupyter_notebook_config.py /etc/jupyter/

# Install openhexa-sdk & openhexa-toolbox
ENV HEXA_ENVIRONMENT CLOUD_JUPYTER


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
