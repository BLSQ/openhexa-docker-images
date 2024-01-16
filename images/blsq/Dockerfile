FROM blsq/openhexa-base-environment

USER root

# System libraries
RUN apt-get update

# For rgdal & sf (R)
RUN apt-get install -y libgdal-dev libudunits2-dev

USER ${NB_UID}
WORKDIR $HOME

# RUN conda update --force conda

RUN mamba install --yes -c conda-forge \
  # Python packages
  'dask-ml' \
  'descartes' \
  'geoalchemy2' \
  'geopandas' \
  'lerc' \
  'plotly' \
  'slack_sdk' \
  'mapclassify' \
  'rasterstats' \
  # R Packages
  'r-rgdal' \
  'r-rgeos' \
  'r-rgooglemaps' \
  'r-geojsonio' \
  'r-ggmap' \
  'r-ggthemes' \
  'r-hmisc' \
  'r-maptools' \
  'r-plotly' \
  'r-raster' \
  'r-sf' 
  # && mamba clean --yes --all


RUN echo "$(conda list)"

