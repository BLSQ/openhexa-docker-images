FROM quay.io/jupyter/datascience-notebook:2024-01-08

USER root

# System libraries
RUN apt-get update

# FUSE Amazon S3
RUN sudo apt-get install -y s3fs

# FUSE Google Cloud Storage
RUN apt-get install -y \
  gnupg \
  lsb-release && \
  gcsFuseRepo=gcsfuse-`lsb_release -c -s` && \
  echo "deb https://packages.cloud.google.com/apt $gcsFuseRepo main" | \
  tee /etc/apt/sources.list.d/gcsfuse.list && \
  curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
  apt-key add - && \
  apt-get update && \
  apt-get install -y gcsfuse && \
  apt-get clean

WORKDIR $HOME

# Add locales
RUN locale-gen fr_FR fr_FR.UTF-8 es_ES es_ES.UTF-8 de_DE de_DE.UTF-8
RUN update-locale

# Install AWS CLI tools
RUN mkdir -p /usr/local/src/awcli
WORKDIR /usr/local/src/awcli
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
WORKDIR $HOME
RUN rm -rf /usr/local/src/awcli

# /home/hexa symlink (preferred path for data pipelines)
RUN ln -s /home/jovyan /home/hexa
RUN chown jovyan /home/hexa

USER ${NB_UID}

# R packages (only available on cran)
RUN R -e "install.packages('GISTools', dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/')"
RUN R -e "install.packages('OpenStreetMap', dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/')"

# R packages (mamba + conda-forge)
RUN mamba install --yes -c conda-forge \
  'r-arrow=14.*' \
  'r-getpass=0.*' \
  'r-readxl=1.*' \
  'r-isotree=0.5.*' \ 
  'r-rcolorbrewer=1.*' \
  'r-rjson=0.2.*' \
  'r-rpostgres=1.*' \
  'r-styler=1.*' \
  'r-tidyverse=2.*' \
  'r-viridis=0.6.*' \
  'r-nloptr=2.*' \
  && mamba clean --yes --all

RUN mamba install --yes -c R \
  'r-imputets=3.*'  \
  'r-tsbox=0.3.*' \
  'r-mmwrweek=0.1.*' \
  && mamba clean --yes --all


# Python packages (mamba + conda-forge)
RUN mamba install --yes -c conda-forge \
  'black=23.12.*' \
  'fsspec=2023.12.2' \
  'gcsfs=2023.12.2' \
  'ipywidgets=8.*' \
  'isort=5.*' \
  'lxml=5.*' \
  'nbresuse=0.4.*' \
  'netCDF4=1.*' \
  'papermill=2.*' \
  'polars=0.20.*' \
  'psycopg2=2.*' \
  'pyarrow=14.*' \
  'rapidfuzz=3.*' \
  'rpy2=3.*' \
  'xarray=2023.12.0' \
  'zarr=2.*' \
  'contextily=1.*' \
  'tabpy=2.*' \
  'docxtpl=0.11.*' \
  # Jupyter extensions
  'jupyterlab-git=0.*' \
  'jupyter-resource-usage=1.*' \
  'jupyterlab_code_formatter=2.*' \
  && mamba clean --yes --all


# Build Jupyterlab - needed for extensions
RUN jupyter lab build -y && \
  jupyter lab clean -y && \
  npm cache clean --force && \
  rm -rf "/home/${NB_USER}/.cache/yarn"

# custom config
COPY jupyter_notebook_config.py /etc/jupyter/

# Install openhexa-sdk & openhexa-toolbox
ENV HEXA_ENVIRONMENT CLOUD_JUPYTER
RUN pip install -U \
  'openhexa-sdk==0.1.33' \
  'openhexa-toolbox==0.1.7'

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

# Redefine the entrypoint to be able to launch pipelines as well
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD singleuser
