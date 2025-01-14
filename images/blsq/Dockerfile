FROM blsq/openhexa-base-environment

LABEL org.opencontainers.image.source=https://github.com/blsq/openhexa-docker-images
LABEL org.opencontainers.image.description="OpenHEXA Jupyter Notebook image with additional tools and libraries specific to BLSQ use cases."
LABEL org.opencontainers.image.licenses=MIT

USER root

# System libraries
RUN apt-get update && apt-get install -y libgdal-dev libudunits2-dev

# R packages (only available on cran)
RUN R -e "options(Ncpus = parallel::detectCores()); install.packages(c('GISTools', 'OpenStreetMap'), dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/', Ncpus=parallel::detectCores())"

USER ${NB_UID}
WORKDIR $HOME

# Install additional Python and R packages
RUN conda install --yes  -c conda-forge -c R \
  # Python packages
  'ruff' \
  'boto3' \
  'python-kaleido' \
  'dateparser' \
  'dask-ml' \
  'descartes' \
  'geoalchemy2' \
  'geopandas' \
  'lerc' \
  'plotly' \
  'slack_sdk' \
  'mapclassify' \
  'rasterstats' \
  'connectorx' \
  'xlsx2csv' \
  'xlsxwriter' \
  'black' \
  'ipywidgets' \
  'isort' \
  'lxml' \
  'nbresuse' \
  'netCDF4' \
  'polars' \
  'psycopg2' \
  'pyarrow' \
  'rapidfuzz' \
  'xarray' \
  'zarr' \
  'contextily' \
  'tabpy' \
  'docxtpl' \
  # R Packages
  'r-arrow' \
  'r-getpass' \
  'r-readxl' \
  'r-isotree' \
  'r-rcolorbrewer' \
  'r-rjson' \
  'r-rpostgres' \
  'r-styler' \
  'r-viridis'  \
  'r-nloptr' \
  'r-rgeos' \
  'r-rgooglemaps' \
  'r-ggmap' \
  'r-ggthemes' \
  'r-hmisc' \
  'r-maptools' \
  'r-plotly' \
  'r-raster' \
  'r-sf' \
  'r-stringi' \
   && conda clean --all -y

# Set PYTHONUNBUFFERED to ensure that Python output is sent straight to terminal
ENV PYTHONUNBUFFERED=1
# Set RUFF_CACHE_DIR env variable
ENV RUFF_CACHE_DIR=/tmp/.ruff_cache
