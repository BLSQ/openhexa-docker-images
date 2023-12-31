FROM jupyter/datascience-notebook:2023-01-24

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

# For rgdal & sf (R)
RUN apt-get install -y libgdal-dev libudunits2-dev

# /home/hexa symlink (preferred path for data pipelines)
RUN ln -s /home/jovyan /home/hexa
RUN chown jovyan /home/hexa

USER ${NB_UID}

# R packages (mamba + conda-forge)
RUN mamba install --yes -c conda-forge \
    'r-arrow=11.0.0' \
    'r-aws.s3=0.*' \
    'r-geojsonio=0.*' \
    'r-getpass=0.*' \
    'r-ggmap=3.*' \
    'r-ggthemes=4.*' \
    'r-hmisc=4.*' \
    'r-maptools=1.*' \
    'r-plotly=4.*' \
    'r-raster=3.*' \
    'r-readxl=1.*' \
    'r-rcolorbrewer=1.*' \
    'r-rgdal=1.*' \
    'r-rgeos=0.*' \
    'r-rgooglemaps=1.*' \
    'r-rjava=1.*' \
    'r-rjson=0.*' \
    'r-rpostgres=1.*' \
    'r-sf=1.*' \
    'r-styler=1.*' \
    'r-tidyverse=1.*' \
    'r-viridis=0.*' \
    'r-nloptr' \
    && mamba clean --yes --all

# R packages (cran)
RUN R -e "install.packages('GISTools', dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/')"
RUN R -e "install.packages('OpenStreetMap', dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/')"
RUN R -e "install.packages('isotree', dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/')"
RUN R -e "install.packages('MMWRweek', dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/')"
RUN R -e "install.packages('imputeTS', dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/')"
RUN R -e "install.packages('tsbox', dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/')"

# Python packages (mamba + conda-forge)
RUN mamba install --yes -c conda-forge \
    'lerc=4.*' \
    'black=22.*' \
    'dask-ml=2022.*' \
    'descartes=1.*' \
    'fsspec=2022.*' \
    'gcsfs=2022.*' \
    'geoalchemy2=0.*' \
    'geopandas=0.*' \
    'hybridcontents=0.*' \
    'ipywidgets=7.*' \
    'isort=5.*' \
    'lxml=4.*' \
    'mapclassify=2.*' \
    'nbresuse=0.*' \
    'netCDF4=1.*' \
    'papermill==2.*' \
    'plotly=5.*' \
    'psycopg2=2.*' \
    'pyarrow=11.0.0' \
    'rapidfuzz=2.*' \
    'rasterstats=0.*' \
    'rpy2=3.*' \
    's3contents=0.*' \
    's3fs=2022.*' \
    'slack_sdk=3.*' \
    'xarray=2022.*' \
    'zarr=2.*' \
    'polars=0.*' \
    && mamba clean --yes --all

# Python packages (pip)
RUN pip install -U \
    'contextily==1.*' \
    'cowsay==4.*' \
    'docxtpl==0.*' \
    'fake-useragent==0.*' \
    'hdx-python-api==5.*' \
    'requests' \
    'tabpy==2.*'

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