FROM blsq/openhexa-base-environment

USER root

# System libraries
RUN apt-get update
# For rgdal & sf (R)
RUN apt-get install -y libgdal-dev libudunits2-dev

# Install AWS CLI tools
RUN mkdir -p /usr/local/src/awscli
WORKDIR /usr/local/src/awscli
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
  unzip awscliv2.zip && \
  ./aws/install

WORKDIR $HOME
RUN rm -rf /usr/local/src/awscli

# Set PYTHONUNBUFFERED to ensure that Python output is sent straight to terminal
ENV PYTHONUNBUFFERED=1

USER ${NB_UID}
WORKDIR $HOME

# R packages (only available on cran)
RUN R -e "install.packages('GISTools', dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/')" && \
    R -e "install.packages('OpenStreetMap', dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/')"


RUN  conda install --yes -c conda-forge \
  # Override base packages (we need to downgrade some of them)
  'fsspec=2022.*' \
  'gcsfs=2022.*' \
  # Blsq Python packages
  'dask-ml=2022.5.27' \
  'descartes=1.*' \
  'geoalchemy2=0.14.*' \
  'geopandas=0.14.*' \
  'lerc=4.*' \
  'plotly=5.*' \
  'slack_sdk=3.*' \
  'mapclassify=2.*' \
  'rasterstats=0.19.*' \
  # Legacy Python packages
  's3contents' \
  's3fs=2022.*' \
  'hybridcontents=0.3.*' \
  'fake-useragent==1.4.*' \
  'hdx-python-api==6.*' \
  # R Packages
  'r-rgdal=1.*' \
  'r-rgeos=0.6.*' \
  'r-rgooglemaps=1.*' \
  'r-geojsonio=0.11.*' \
  'r-ggmap=3.*' \
  'r-ggthemes=4.*' \
  'r-hmisc=4.*' \
  'r-maptools=1.*' \
  'r-plotly=4.*' \
  'r-raster=3.*' \
  'r-sf=1.*' \
  # Legacy R packages
  'r-rjava=1.*' \
  'r-aws.s3=0.3.*' \
  # Legacy Jupyter extensions
  'dash=2.*' \
  'jupyter-server-proxy=4.*' && \
  conda clean --all -y

# k8s: same as sample files, we need to copy those to a temp location
COPY files/scripts/* /tmp/hexa_scripts/
# Please note that if a PVC is mounted at /home/jovyan (for OpenHEXA legacy notebooks), this directory will be
# "lost" - they need to be copied again from /tmp after mounting the PVC
COPY files/scripts/* /home/jovyan/.hexa_scripts/

# sample files
# k8s: stored in /tmp within the pod, then copied back in the home directory after the PVC has been mounted through
# a postStart hook defined in config.yaml, and also by the wrap_up.py file
# TODO: postStart hook should not be necessary anymore
# (see https://zero-to-jupyterhub.readthedocs.io/en/latest/customizing/user-environment.html#about-user-storage-and-adding-files-to-it)
COPY files/sample_files/* /tmp/notebooks_sample_files/


# Build Jupyterlab - needed for extensions
RUN jupyter lab build -y && \
  jupyter lab clean -y && \
  npm cache clean --force && \
  rm -rf "/home/${NB_USER}/.cache/yarn"
