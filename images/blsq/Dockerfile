ARG BASE_IMAGE=blsq/openhexa-base-environment

FROM ${BASE_IMAGE}

USER root

# System libraries
RUN apt-get update && apt-get install -y libgdal-dev libudunits2-dev

USER ${NB_UID}

RUN ls -la /home/jovyan

# Install packages in batches to avoid too high memory consumption
RUN mamba install --yes  -c conda-forge \
    # Python packages
    'black' \
    'boto3' \
    'connectorx' \
    'dask-ml' \
    'dateparser' \
    'docxtpl' \
    'isort' \
    'lerc' \
    'lxml' \
    'nbresuse' \
    'netCDF4' \
    'plotly' \
    'polars' \
    'pyarrow' \
    'python-kaleido' \
    'rapidfuzz' \
    'ruff' \
    'slack_sdk' \
    'tabpy' \
    'xarray' \
    'xlsx2csv' \
    'xlsxwriter' \
    'zarr' \
  && mamba install --yes  -c conda-forge \
    # Spatial/GIS packages
    'contextily' \
    'descartes' \
    'geoalchemy2' \
    'geopandas' \
    'mapclassify' \
    'rasterstats' \
  && mamba install --yes -c conda-forge -c R \
    # R packages: We set up a minimal R environment to be able to use this image as a base for the workspaces
    'r-base' \
    'r-arrow' \
    'r-getpass' \
    'r-ggmap'\
    'r-ggthemes' \
    'r-irkernel' \
    'r-maptools' \
    'r-nloptr' \
    'r-plotly' \
    'r-raster' \
    'r-rcolorbrewer' \
    # one of these has an issue?
    'r-readxl' \
    'r-rgeos' \
    'r-rgooglemaps' \
    'r-rjson' \
    'r-rpostgres' \
    'r-sf' \
    'r-stringi' \
    'r-styler' \
    'r-viridis' \
  && mamba clean --all -f -y \
  && fix-permissions "${CONDA_DIR}"

# R packages (only available on cran)
RUN R -e "options(Ncpus = parallel::detectCores()); install.packages(c('GISTools', 'OpenStreetMap'), dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/', Ncpus=parallel::detectCores())"

WORKDIR $HOME

# Set PYTHONUNBUFFERED to ensure that Python output is sent straight to terminal
ENV PYTHONUNBUFFERED=1
# Set RUFF_CACHE_DIR env variable
ENV RUFF_CACHE_DIR=/tmp/.ruff_cache
# Set PROJ_LIB env variable needed by the R sf package
ENV PROJ_LIB=/opt/conda/share/proj
