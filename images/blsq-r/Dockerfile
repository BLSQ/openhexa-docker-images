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
RUN mamba install --yes -c conda-forge \
    r-arrow \
    r-irkernel \
    r-tidyverse \
    r-getpass \
    r-readxl \
    r-rcolorbrewer \
    r-rjson \
    r-rpostgres \
    r-styler \
    r-viridis \
    r-nloptr \
    r-rgeos \
    r-rgooglemaps \
    r-ggmap \
    r-ggthemes \
    r-maptools \
    r-plotly \
    r-raster \
    r-sf \
    r-stringi \
    r-glue \
    r-here \
    r-lubridate \
    r-forcats \
    r-stringr \
    r-dplyr \
    r-purrr \
    r-readr \
    r-tidyr \
    r-tibble \
    r-ggplot2 \
    r-gtable \
    r-websocket \
    r-processx \
    r-tzdb \
    r-ps \
    r-vctrs \
    r-generics \
    r-proxy \
    r-fansi \
    r-pkgconfig \
    r-kernsmooth \
    r-lifecycle \
    r-farver \
    r-munsell \
    r-httpuv \
    r-sass \
    r-htmltools \
    r-rttf2pt1 \
    r-later \
    r-pillar \
    r-crayon \
    r-classint \
    r-mime \
    r-tidyselect \
    r-digest \
    r-labeling \
    r-rprojroot \
    r-fastmap \
    r-colorspace \
    r-cli \
    r-magrittr \
    r-utf8 \
    r-rlang \
    r-rcpp \
    r-dbi \
    r-xml \
    r-xml2 \
    r-renv \
    r-jsonlite \
    r-rstudioapi \
    r-e1071 \
    r-withr \
    r-promises \
    r-scales \
    r-bit64 \
    r-timechange \
    r-bit \
    r-qpdf \
    r-hms \
    r-pagedown \
    r-vroom \
    r-r6 \
    r-fs \
    r-systemfonts \
    r-units \
    r-askpass \
    r-ragg \
    r-textshaping \
    && mamba clean --all -y && \
    fix-permissions "${CONDA_DIR}"


# R packages (only available on cran)
RUN R -e "options(Ncpus = parallel::detectCores()); install.packages(c('GISTools', 'OpenStreetMap'), dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/', Ncpus=parallel::detectCores())"

USER ${NB_UID}
WORKDIR $HOME

# Set PROJ_LIB env variable needed by the R sf package
ENV PROJ_LIB=/opt/conda/share/proj
