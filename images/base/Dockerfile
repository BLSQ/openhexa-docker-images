FROM jupyter/datascience-notebook:2023-10-20

USER root

# System libraries
RUN apt-get update

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

# /home/hexa symlink (preferred path for data pipelines)
RUN ln -s /home/jovyan /home/hexa
RUN chown jovyan /home/hexa

USER ${NB_UID}

# Python packages (mamba + conda-forge)
RUN mamba install --yes -c conda-forge \
    'black=22.*' \
    'fsspec=2022.*' \
    'gcsfs=2022.*' \
    'isort=5.*' \
    'papermill==2.*' \
    'plotly=5.*' \
    'psycopg2=2.*' \
    && mamba clean --yes --all

# Python packages (pip)
RUN pip install -U \
    'requests'

# Jupyter extensions
RUN mamba install -c conda-forge --yes \
    'dash=2.*' \
    'jupyter-resource-usage=0.*' \
    'jupyterlab_code_formatter=1.*' \
    && mamba clean --yes --all

# Build Jupyterlab - needed for extensions
RUN jupyter lab build -y && \
    jupyter lab clean -y && \
    npm cache clean --force && \
    rm -rf "/home/${NB_USER}/.cache/yarn"

# Custom config
COPY jupyter_notebook_config.py /etc/jupyter/

# Install openhexa-sdk & openhexa-toolbox
ENV HEXA_ENVIRONMENT CLOUD_JUPYTER
RUN pip install -U \
    'openhexa-sdk==0.1.33' \
    'openhexa-toolbox==0.1.7'

# Fuse
COPY files/scripts/fuse.conf /etc/.
COPY files/scripts/* /home/jovyan/.hexa_scripts/

COPY files/sample_files/* /home/jovyan/.

# Copy the entrypoint at the same location as the ones defined in the base image
COPY entrypoint.sh /usr/local/bin/

# Redefine the entrypoint to be able to launch pipelines as well
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD singleuser