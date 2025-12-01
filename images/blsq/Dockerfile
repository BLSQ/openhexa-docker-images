ARG BASE_IMAGE=blsq/openhexa-base-environment

FROM ${BASE_IMAGE}

USER root

# System libraries
RUN apt-get update && apt-get install -y libgdal-dev libudunits2-dev

USER ${NB_UID}

RUN ls -la /home/jovyan
# Install additional Python and R packages.
# Split into batches to avoid running out of memory.
RUN mamba install --yes -c conda-forge \
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
    'pyarrow' \
    'rapidfuzz' \
    'xarray' \
    'zarr' \
    'contextily' \
    'tabpy' \
    'docxtpl' \
  && mamba install --yes -c conda-forge -c R \
    # R : We setup a minimal R environment to be able to use this image as a base for the workspaces
    'r-base=4.4.*' \
    # R Packages
    'r-irkernel=1.3.*' \
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
  && mamba clean --all -f -y && \
  fix-permissions "${CONDA_DIR}"

# R packages (only available on cran)
RUN R -e "options(Ncpus = parallel::detectCores()); install.packages(c('GISTools', 'OpenStreetMap'), dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/', Ncpus=parallel::detectCores())"

WORKDIR $HOME

# Set PYTHONUNBUFFERED to ensure that Python output is sent straight to terminal
ENV PYTHONUNBUFFERED=1
# Set RUFF_CACHE_DIR env variable
ENV RUFF_CACHE_DIR=/tmp/.ruff_cache
# Set PROJ_LIB env variable needed by the R sf package
ENV PROJ_LIB=/opt/conda/share/proj
