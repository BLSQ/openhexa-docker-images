FROM blsq/openhexa-base-environment

LABEL org.opencontainers.image.source=https://github.com/blsq/openhexa-docker-images
LABEL org.opencontainers.image.description="OpenHEXA Jupyter Notebook image with additional tools and libraries specific to BLSQ use cases."
LABEL org.opencontainers.image.licenses=MIT

USER root

# System libraries
RUN apt-get update && apt-get install -y libgdal-dev libudunits2-dev

USER ${NB_UID}
WORKDIR $HOME

RUN conda install --yes -c conda-forge \
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
  'connectorx==0.3.*' \
  'xlsx2csv==0.8.*' \
  'xlsxwriter==3.*' \
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
  'r-stringi=1.*' &&\
  conda clean --all -y

# Set PYTHONUNBUFFERED to ensure that Python output is sent straight to terminal
ENV PYTHONUNBUFFERED=1