FROM blsq/openhexa-blsq-environment

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


RUN R -e "install.packages('ggnewscale', dependencies=TRUE, quiet=TRUE, repos='https://cran.r-project.org/')" 



RUN conda install --yes -c R  \
  'r-extrafont'  \
  'r-glue'  \
  'r-here'  \
  'r-lubridate'  \
  'r-forcats'  \
  'r-stringr'  \
  'r-dplyr'  \
  'r-purrr'  \
  'r-readr'  \
  'r-tidyr'  \
  'r-tibble'  \
  'r-ggplot2'  \
  'r-gtable'  \
  'r-websocket'  \
  'r-processx'  \
  'r-tzdb'  \
  'r-ps'  \
  'r-vctrs'  \
  'r-generics'  \
  'r-proxy'  \
  'r-fansi'  \
  'r-pkgconfig'  \
  'r-kernsmooth'  \
  'r-lifecycle'  \
  'r-farver'  \
  'r-munsell'  \
  'r-httpuv'  \
  'r-sass'  \
  'r-htmltools'  \
  'r-rttf2pt1'  \
  'r-later'  \
  'r-pillar'  \
  'r-crayon'  \
  'r-classint'  \
  'r-mime'  \
  'r-tidyselect'  \
  'r-digest'  \
  'r-stringi'  \
  'r-labeling'  \
  'r-rprojroot'  \
  'r-fastmap'  \
  'r-colorspace'  \
  'r-cli'  \
  'r-magrittr'  \
  'r-utf8'  \
  'r-e1071'  \
  'r-withr'  \
  'r-promises'  \
  'r-scales'  \
  'r-bit64'  \
  'r-timechange'  \
  'r-bit'  \
  'r-qpdf'  \
  'r-pagedown'  \
  'r-askpass'  \
  'r-hms'  \
  'r-rlang'  \
  'r-rcpp'  \
  'r-dbi'  \
  'r-xml2'  \
  'r-renv'  \
  'r-jsonlite'  \
  'r-rstudioapi'  \
  'r-vroom'  \
  'r-r6'  \
  'r-fs'  \
  'r-systemfonts'  \
  'r-units'  && \
  conda clean --all -y