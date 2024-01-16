FROM blsq/openhexa-base-environment

USER root

# System libraries
RUN apt-get update
# For rgdal & sf (R)
RUN apt-get install -y libgdal-dev libudunits2-dev


USER ${NB_UID}
WORKDIR $HOME

RUN mamba install --yes -c conda-forge \
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
  's3contents=0.9.*' \
  's3fs=2021.*' \
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
  'jupyter-server-proxy=4.*' \
  && mamba clean --yes --all


# Build Jupyterlab - needed for extensions
RUN jupyter lab build -y && \
  jupyter lab clean -y && \
  npm cache clean --force && \
  rm -rf "/home/${NB_USER}/.cache/yarn"
