FROM blsq/openhexa-base-environment

LABEL org.opencontainers.image.source=https://github.com/blsq/openhexa-docker-images
LABEL org.opencontainers.image.description="OpenHEXA Jupyter Notebook image with additional tools and libraries specific to BLSQ use cases."
LABEL org.opencontainers.image.licenses=MIT

USER root

# System libraries
RUN apt-get update && apt-get install -y libgdal-dev libudunits2-dev

# Install additional Python and R packages
RUN conda install --yes  -c conda-forge -c R \
  # Python packages
  'ruff=0.9.*' \
  'boto3=1.35.*' \
  'python-kaleido=0.2.*' \
  'dateparser=1.2.*' \
  'dask-ml=2022.5.27' \
  'descartes=1.*' \
  'geoalchemy2=0.14.*' \
  'geopandas=1.0.*' \
  'lerc=4.*' \
  'plotly=5.*' \
  'slack_sdk=3.*' \
  'mapclassify=2.*' \
  'rasterstats=0.19.*' \
  'connectorx==0.3.*' \
  'xlsx2csv==0.8.*' \
  'xlsxwriter==3.*' \
  'black=23.12.*' \
  'ipywidgets=8.*' \
  'isort=5.*' \
  'lxml=5.*' \
  'nbresuse=0.4.*' \
  'netCDF4=1.*' \
  'polars=0.20.*' \
  'psycopg2=2.*' \
  'pyarrow=18.1.*' \
  'rapidfuzz=3.*' \
  'xarray=2025.1.1' \
  'zarr=2.*' \
  'contextily=1.*' \
  'tabpy=2.*' \
  'docxtpl=0.11.*' \
  # R Packages
  'r-arrow=18.1.*' \
  'r-getpass=0.*' \
  'r-readxl=1.*' \
  'r-rcolorbrewer=1.*' \
  'r-rjson=0.2.*' \
  'r-rpostgres=1.4.*' \
  'r-styler=1.*' \
  'r-viridis=0.6.*' \
  'r-nloptr=2.*' \
  'r-rgeos=0.*' \
  'r-rgooglemaps=1.5.*' \
  'r-ggmap=4.0.*'\
  'r-ggthemes=5.1.*' \
  'r-maptools=1.*' \
  'r-plotly=4.*' \
  'r-raster=3.*' \
  'r-sf=1.*' \
  'r-stringi=1.*' \
  && conda clean --all -y

  
# R packages (only available on cran)
RUN R -e "options(Ncpus = parallel::detectCores()); install.packages(c('GISTools', 'OpenStreetMap'), dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/', Ncpus=parallel::detectCores())"
  
USER ${NB_UID}
WORKDIR $HOME

# Set PYTHONUNBUFFERED to ensure that Python output is sent straight to terminal
ENV PYTHONUNBUFFERED=1
# Set RUFF_CACHE_DIR env variable
ENV RUFF_CACHE_DIR=/tmp/.ruff_cache
