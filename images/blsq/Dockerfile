FROM blsq/openhexa-base-environment

USER root

# System libraries
RUN apt-get update

# For rgdal & sf (R)
RUN apt-get install -y libgdal-dev libudunits2-dev

USER ${NB_UID}
WORKDIR $HOME

RUN mamba install --yes -c conda-forge \
  # Python packages
  'dask-ml=2022.5.27' \
  'descartes=1.*' \
  'geoalchemy2=0.14.*' \
  'geopandas=0.14.*' \
  'lerc=4.*' \
  'plotly=5.*' \
  'slack_sdk=3.*' \
  'mapclassify=2.*' \
  'rasterstats=0.19.*' \
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
  && mamba clean --yes --all

