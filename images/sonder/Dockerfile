FROM blsq/openhexa-base-environment
LABEL org.opencontainers.image.source=https://github.com/blsq/openhexa-docker-images
LABEL org.opencontainers.image.description="Pathways Jupyter Notebook image with additional tools and libraries specific to Pathways use cases."
LABEL org.opencontainers.image.licenses=MIT
USER root
# System libraries
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt-get update && apt-get install -y libgdal-dev libudunits2-dev
USER ${NB_UID}
WORKDIR $HOME

RUN conda install --yes -c conda-forge \
    r-abind=1.4.* \
    r-base \
    r-base64enc=0.1.* \
    r-bit64=4.6.* \
    r-bitops=1.0.* \
    r-broom=1.0.* \
    r-biocmanager=1.30.* \
    r-cachem=1.1.* \
    r-callr=3.7.* \
    r-cardata=3.0.* \
    r-caret=6.* \
    r-cellranger=1.1.* \
    r-checkmate=2.3.* \
    r-class \
    r-classint \
    r-cli=3.6.* \
    r-clipr \
    r-clock \
    r-coda \
    r-codetools \
    r-colorspace=2.* \
    r-commonmark \
    r-config=0.3.* \
    r-conflicted \
    r-corrplot=0.* \
    r-cowplot=1.1.* \
    r-cpp11 \
    r-crayon \
    r-crosstalk \
    r-curl \
    r-data.table=1.15.* \
    r-dbi \
    r-dendextend \
    r-deriv \
    r-diagram \
    r-digest \
    r-doby \
    r-dplyr=1.1.* \
    r-e1071 \
    r-ellipse \
    r-emmeans \
    r-estimability \
    r-evaluate \
    r-factoextra=1.0.* \
    r-fansi \
    r-farver \
    r-fastdummies=1.7.* \
    r-fastmap \
    r-foreign=0.* \
    r-fontawesome \
    r-forcats=1.0.* \
    r-generics \
    r-ggcorrplot \
    r-ggdist \
    r-ggforce=0.4.* \
    r-ggmap=4.0.* \
    r-ggplot2=3.5.* \
    r-ggpubr=0.6.* \
    r-ggrepel=0.9.* \
    r-ggsignif \
    r-ggthemes=5.1.* \
    r-globals \
    r-glue \
    r-gower \
    r-gridExtra=2.* \
    r-gtable \
    r-hardhat \
    r-haven=2.5.* \
    r-highr \
    r-hms \
    r-htmltools \
    r-htmlwidgets \
    r-httpuv \
    r-huxtable=5.5.* \
    r-igraph \
    r-insight \
    r-ipred \
    r-irkernel=1.3.* \
    r-isoband \
    r-iterators \
    r-jtools=2.2.* \
    r-jsonlite \
    r-kernsmooth \
    r-knitr \
    r-labeling \
    r-later \
    r-lattice \
    r-lava \
    r-lazyeval \
    r-leaps \
    r-lifecycle \
    r-listenv \
    r-lme4 \
    r-lubridate \
    r-magick \
    r-magrittr=2.0.* \
    r-maptools=1.* \
    r-mass \
    r-matrix \
    r-matrixmodels \
    r-memoise \
    r-mgcv \
    r-microbenchmark \
    r-mime \
    r-minqa \
    r-mitools \
    r-modelmetrics \
    r-modelr \
    r-modelsummary=2.2.* \
    r-multcompview \
    r-munsell \
    r-mvtnorm \
    r-networkd3 \
    r-nlme \
    r-nloptr \
    r-openxlsx=4.2.5.* \
    r-pacman \
    r-pander \
    r-parameters \
    r-pbkrtest \
    r-performance \
    r-pillar \
    r-pkgconfig \
    r-plotly=4.* \
    r-poLCA=1.6.0.* \
    r-polyclip \
    r-polynom \
    r-prettyunits \
    r-processx \
    r-prodlim \
    r-progress \
    r-progressr \
    r-promises \
    r-proxy \
    r-ps \
    r-purrr=1.0.* \
    r-quadprog \
    r-quantreg \
    r-r6 \
    r-rappdirs \
    r-raster=3.* \
    r-rbibutils \
    r-rcolorbrewer=1.* \
    r-rcpp \
    r-rcpparmadillo \
    r-rcppeigen \
    r-rdpack \
    r-readr \
    r-readstata13=0.10.* \
    r-readxl=1.4.* \
    r-recipes \
    r-rematch \
    r-remotes \
    r-renv \
    r-reshape2=1.4.* \
    r-reticulate=1.40.* \
    r-rgeos=0.* \
    r-rgooglemaps=1.5.* \
    r-rmarkdown \
    r-rpart=4.1.* \
    r-rpart.plot=3.1.* \
    r-rpostgres=1.4.* \
    r-rstudioapi \
    r-s2 \
    r-sandwich \
    r-sass \
    r-scales \
    r-scatterpie \
    r-scatterplot3d \
    r-shape \
    r-shiny \
    r-sf=1.* \
    r-sourcetools \
    r-sparsem \
    r-squarem \
    r-stringi=1.* \
    r-stringr=1.5.* \
    r-survival \
    r-svyVGAM=1.* \
    r-systemfonts \
    r-tables \
    r-tibble=3.2.* \
    r-tidyr=1.3.* \
    r-tidyselect \
    r-timeDate \
    r-timechange \
    r-tinytex \
    r-tweenr \
    r-tzdb \
    r-units \
    r-utf8 \
    r-viridis=0.6.* \
    r-viridislite \
    r-vroom \
    r-webshot \
    r-withr \
    r-wk \
    r-xfun \
    r-xtable \
    r-yaml=2.3.* \
    r-yulab.utils=0.2.* \
    r-zip=2.3.*\
    r-zoo 

RUN conda clean --all -y

# Additional CRAN packages not available on conda-forge
RUN R -e "options(Ncpus = parallel::detectCores()); install.packages(c('bayestestR', 'datawizard', 'distributional', 'ggradar', 'tinytable', 'bibutils', 'rsurvey', 'reformulate', 'servyr', 'zscorer'), repos='https://cran.r-project.org/', dependencies=TRUE)"