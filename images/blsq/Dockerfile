ARG BASE_IMAGE=blsq/openhexa-base-environment

FROM ${BASE_IMAGE}

USER root

# System libraries
RUN apt-get update && apt-get install -y libgdal-dev libudunits2-dev odbc-mdbtools

# AI tooling: Claude Code and Gemini CLI.
# HOME is /home/jovyan even for root here: give npm a throwaway home so it does
# not leave a root-owned ~/.npm behind, which the notebook user could not use.
RUN HOME=/tmp/npm-home npm install -g @anthropic-ai/claude-code @google/gemini-cli && \
    rm -rf /tmp/npm-home

USER ${NB_UID}

RUN ls -la /home/jovyan
# Install additional Python and R packages.
# Split into batches to avoid running out of memory.
# r-getpass r-rpostgres have no linux-aarch64 build on conda-forge: on arm64,
# getPass and RPostgres come from CRAN (below), built against conda's libpq.
RUN if [ "$(uname -m)" = x86_64 ]; then \
      arch_pkgs="r-getpass r-rpostgres"; \
    else \
      arch_pkgs="libpq"; \
    fi && \
    mamba install --yes -c conda-forge \
    # Python packages
    # Pin sqlite: geo stack otherwise drags in the old monolithic 3.32.3, breaking import sqlite3.
    'sqlite>=3.49' \
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
    'pyodbc' \
  && mamba install --yes -c conda-forge -c R \
    # Pin sqlite here too: the R batch re-downgrades it to 3.32.3 within this same layer.
    'sqlite>=3.49' \
    # R : We setup a minimal R environment to be able to use this image as a base for the workspaces
    'r-base=4.5.*' \
    # R Packages
    'r-irkernel' \
    'r-arrow' \
    'r-readxl' \
    'r-rcolorbrewer' \
    'r-rjson' \
    'r-styler' \
    'r-viridis' \
    'r-nloptr' \
    # r-rgeos and r-maptools dropped: retired from CRAN
    'r-rgooglemaps' \
    'r-ggmap' \
    'r-ggthemes' \
    'r-plotly' \
    'r-raster' \
    'r-sf' \
    'r-stringi' \
    # r-httr2 for the OpenHEXA R SDK (below)
    'r-httr2' \
    # rJava for OpenStreetMap (CRAN, below): building it from source fails
    # against conda's R, which points at the Java of its own build machine.
    'r-rjava' \
    ${arch_pkgs} \
  && mamba clean --all -f -y && \
  fix-permissions "${CONDA_DIR}"

# R packages (only available on cran). install.packages() only warns when a
# package fails, so check they all load and fail the build otherwise.
RUN R -e "options(Ncpus = parallel::detectCores()); install.packages(c('GISTools', 'OpenStreetMap'), dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/', Ncpus=parallel::detectCores())" \
    && R -e "pkgs <- c('GISTools', 'OpenStreetMap'); missing <- pkgs[!vapply(pkgs, requireNamespace, logical(1), quietly = TRUE)]; if (length(missing)) stop('CRAN packages failed to install: ', paste(missing, collapse = ', '))"

# On arm64, the packages that have no linux-aarch64 build on conda-forge (see
# the R batch above), with their required dependencies only.
RUN if [ "$(uname -m)" != x86_64 ]; then \
      R -e "install.packages(c('getPass', 'RPostgres'), quiet=TRUE, repos='https://cran.r-project.org/', Ncpus=parallel::detectCores())" && \
      R -e "pkgs <- c('getPass', 'RPostgres'); missing <- pkgs[!vapply(pkgs, requireNamespace, logical(1), quietly = TRUE)]; if (length(missing)) stop('CRAN packages failed to install: ', paste(missing, collapse = ', '))"; \
    fi

# The OpenHEXA R SDK, pinned to a release of https://github.com/BLSQ/openhexa-sdk-r.
# r-httr2 comes from conda above, its other imports with the R packages there:
# repos = NULL installs the archive alone, and the check fails the build if the
# package or one of its dependencies is missing. Also installed in blsq-r:
# Renovate bumps both in the same PR.
# renovate: datasource=github-releases depName=BLSQ/openhexa-sdk-r extractVersion=^v(?<version>.*)$
ARG OPENHEXA_R_SDK_VERSION=0.1.1
RUN R -e "install.packages('https://github.com/BLSQ/openhexa-sdk-r/archive/refs/tags/v${OPENHEXA_R_SDK_VERSION}.tar.gz', repos = NULL, type = 'source')" \
    && R -e "if (!requireNamespace('openhexa', quietly = TRUE) || packageVersion('openhexa') != '${OPENHEXA_R_SDK_VERSION}') stop('The openhexa R package failed to install')"

# Attach the OpenHEXA R SDK in every R session, so notebooks can call get_user()
# etc. without library(openhexa). Appended to the Rprofile.site of the Jupyter
# base image, which sets the plot mimetypes.
RUN echo 'options(defaultPackages = c(getOption("defaultPackages"), "openhexa"))' >> "$(R RHOME)/etc/Rprofile.site"

WORKDIR $HOME

# Set PYTHONUNBUFFERED to ensure that Python output is sent straight to terminal
ENV PYTHONUNBUFFERED=1
# Set RUFF_CACHE_DIR env variable
ENV RUFF_CACHE_DIR=/tmp/.ruff_cache
# Symlink MDBTools ODBC driver into conda lib path
RUN ln -s /usr/lib/$(uname -m)-linux-gnu/odbc/libmdbodbc.so /opt/conda/lib/libmdbodbc.so
