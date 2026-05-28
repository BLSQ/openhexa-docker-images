ARG BASE_IMAGE=blsq/openhexa-base-environment

FROM ${BASE_IMAGE}

LABEL org.opencontainers.image.source=https://github.com/blsq/openhexa-docker-images
LABEL org.opencontainers.image.description="OpenHEXA Jupyter Notebook image with additional tools and libraries for R oriented projects."
LABEL org.opencontainers.image.licenses=MIT

USER root

# System libraries
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \ 
    apt-get update && apt-get install -y libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    pandoc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Quarto
RUN wget https://quarto.org/download/latest/quarto-linux-amd64.deb \
    && dpkg -i quarto-linux-amd64.deb \
    && rm quarto-linux-amd64.deb

USER ${NB_UID}

# R 4.5+ on conda-forge is built against icu 78, which matches this image's base
# Python stack (pyarrow, libmamba/conda). Earlier R generations (4.4) link icu
# 75 and would force an icu/pyarrow downgrade that removes conda/mamba, so we pin
# r-base to the 4.5 series and install the R stack directly into the base env.
# r-rgeos and r-maptools are intentionally omitted: both were retired from CRAN
# in 2023 and have no R 4.5 build on conda-forge (their functionality lives on in
# sf/raster). Remaining versions are left unpinned so the resolver can pick a
# self-consistent, icu-78 set.
RUN mamba install --yes -c conda-forge \
    r-base=4.5.* \
    r-irkernel \
    # r-irkernel also pulls in: r-crayon r-digest
    r-arrow \
    r-tidyverse \
    # r-tidyverse also pulls in: r-dplyr r-stringr r-glue r-lubridate r-forcats
    #   r-purrr r-readr r-tidyr r-tibble r-ggplot2 r-readxl r-magrittr r-jsonlite
    #   r-rlang r-cli r-pillar r-hms r-rstudioapi r-xml2 r-ragg r-stringi r-vctrs
    #   r-generics r-tidyselect r-lifecycle r-pkgconfig r-fansi r-utf8 r-r6
    #   r-withr r-scales r-farver r-labeling r-munsell r-colorspace r-gtable
    #   r-tzdb r-vroom r-bit64 r-bit r-timechange r-fs r-systemfonts r-textshaping
    #   r-askpass
    r-getpass \
    r-rcolorbrewer \
    r-rjson \
    r-rpostgres \
    # r-rpostgres also pulls in: r-dbi
    r-styler \
    r-viridis \
    r-nloptr \
    r-rgooglemaps \
    r-ggmap \
    r-ggthemes \
    r-plotly \
    # r-plotly also pulls in: r-htmltools r-promises r-later r-fastmap r-mime
    r-raster \
    # r-raster also pulls in: r-rcpp
    r-sf \
    # r-sf also pulls in: r-classint r-units
    r-here \
    # r-here also pulls in: r-rprojroot
    r-websocket \
    r-processx \
    r-ps \
    r-kernsmooth \
    r-httpuv \
    r-sass \
    r-rttf2pt1 \
    r-xml \
    r-renv \
    r-e1071 \
    # r-e1071 also pulls in: r-proxy
    r-qpdf \
    r-pagedown \
    && mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}"


# R packages (only available on cran)
RUN R -e "options(Ncpus = parallel::detectCores()); install.packages(c('GISTools', 'OpenStreetMap'), dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/', Ncpus=parallel::detectCores())"

USER ${NB_UID}
WORKDIR $HOME

# Set PROJ_LIB env variable needed by the R sf package
ENV PROJ_LIB=/opt/conda/share/proj
