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
RUN conda install --yes  -c conda-forge \
  'r-rpostgres' \
  'r-reticulate' \
  'r-rcolorbrewer' \
  'r-rattle' \
  'r-colorspace' \
  'r-viridis' \
  'r-broom' \
  'r-jtools' \
  'r-openxlsx' \
  'r-ggrepel' \
  'r-tibble' \
  'r-gridExtra' \
  'r-factoextra' \
  'r-modelsummary' \
  'r-poLCA' \
  'r-dplyr' \
  'r-forcats' \
  'r-ggforce' \
  'r-huxtable' \
  'r-purrr' \
  'r-readstata13' \
  'r-svyVGAM' \
  'r-srvyr' \
  'r-rpart' \
  'r-rpart.plot' \
  'r-caret' \
  'r-randomforest' \
  'r-cowplot' \
  'r-ggpubr' \
  'r-fastdummies' \
  'r-corrplot' \
  'r-haven' \
  'r-survey' \
  'r-ggplot2' \
  'r-tidyr' \
  'r-rodbc' \
  'r-readxl' \
  'r-reshape2' \
  'r-data.table' \
  'r-psych' \
  'r-magrittr' \
  'r-stringr' \
  'r-foreign' \
  'r-config' \
  'r-rgeos' \
  'r-rgooglemaps' \
  'r-ggmap' \
  'r-ggthemes' \
  'r-hmisc' \
  'r-maptools' \
  'r-plotly' \
  'r-raster' \
  'r-sf' \
  'r-stringi' &&\ 
  conda clean --all -y