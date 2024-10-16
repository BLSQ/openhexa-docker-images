FROM blsq/openhexa-blsq-environment

LABEL org.opencontainers.image.source=https://github.com/blsq/openhexa-docker-images
LABEL org.opencontainers.image.description="OpenHEXA Jupyter Notebook image with additional tools and libraries for R oriented projects."
LABEL org.opencontainers.image.licenses=MIT

USER root

# System libraries
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \ 
    apt-get update && apt-get install -y  libgdal-dev libudunits2-dev \
    libcurl4-openssl-dev \
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

RUN conda install --yes -c R \
  'r-gt=0.10.*'  \
  'r-extrafont=0.19.*'  \
  'r-glue=1.7.*'  \
  'r-sf=1.0.*'  \
  'r-here=1.0.*'  \
  'r-lubridate=1.9.*'  \
  'r-forcats=1.0.*'  \
  'r-stringr=1.5.*'  \
  'r-dplyr=1.1.*'  \
  'r-purrr=1.0.*'  \
  'r-readr=2.1.*'  \
  'r-tidyr=1.3.*'  \
  'r-tibble=3.2.*'  \
  'r-ggplot2=3.5.*'  \
  'r-tidyverse=2.0.*'  \
  'r-gtable=0.3.*'  \
  'r-websocket=1.4.*'  \
  'r-processx=3.8.*'  \
  'r-tzdb=0.4.*'  \
  'r-ps=1.7.*'  \
  'r-vctrs=0.6.*'  \
  'r-generics=0.1.*'  \
  'r-proxy=0.4.*'  \
  'r-fansi=1.0.*'  \
  'r-pkgconfig=2.0.*'  \
  'r-kernsmooth=2.23.*'  \
  'r-lifecycle=1.0.*'  \
  'r-farver=2.1.*'  \
  'r-textshaping=0.3.*'  \
  'r-munsell=0.5.*'  \
  'r-httpuv=1.6.*'  \
  'r-sass=0.4.*'  \
  'r-htmltools=0.5.*'  \
  'r-rttf2pt1=1.3.*'  \
  'r-later=1.3.*'  \
  'r-pillar=1.9.*'  \
  'r-crayon=1.5.*'  \
  'r-classint=0.4.*'  \
  'r-mime=0.12.*'  \
  'r-tidyselect=1.2.*'  \
  'r-digest=0.6.*'  \
  'r-stringi=1.8.*'  \
  'r-labeling=0.4.*'  \
  'r-rprojroot=2.0.*'  \
  'r-fastmap=1.2.*'  \
  'r-colorspace=2.1.*'  \
  'r-cli=3.6.*'  \
  'r-magrittr=2.0.*'  \
  'r-utf8=1.2.*'  \
  'r-e1071=1.7.*'  \
  'r-withr=3.0.*'  \
  'r-promises=1.3.*'  \
  'r-scales=1.3.*'  \
  'r-bit64=4.0.*'  \
  'r-timechange=0.3.*'  \
  'r-bit=4.0.*'  \
  'r-qpdf=1.3.*'  \
  'r-pagedown=0.20.*'  \
  'r-askpass=1.2.*'  \
  'r-ragg=1.3.*'  \
  'r-hms=1.1.*'  \
  'r-rlang=1.1.*'  \
  'r-rcpp=1.0.*'  \
  'r-dbi=1.2.*'  \
  'r-xml2=1.3.*'  \
  'r-renv=1.0.*'  \
  'r-jsonlite=1.8.*'  \
  'r-rstudioapi=0.16.*'  \
  'r-vroom=1.6.*'  \
  'r-r6=2.5.*'  \
  'r-fs=1.6.*'  \
  'r-systemfonts=1.1.*'  \
  'r-units=0.8.*' &&\
  conda clean --all -y
