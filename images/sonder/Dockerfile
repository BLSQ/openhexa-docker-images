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
  'r-base' \
  'r-irkernel=1.3.*' \
  'r-rpostgres=1.4.*' \
  'r-reticulate=1.40.*'\
  'r-rcolorbrewer=1.*'  \
  'r-rattle=5.5.*' \
  'r-colorspace=2.*' \
  'r-viridis=0.6.*' \
  'r-broom=1.0.*' \
  'r-jtools=2.2.*' \
  'r-openxlsx=4.2.5.*' \
  'r-ggrepel=0.9.*' \
  'r-tibble=3.2.*' \
  'r-gridExtra=2.*' \ 
  'r-factoextra=1.0.*' \
  'r-modelsummary=2.2.*' \
  'r-poLCA=1.6.0.*' \ 
  'r-dplyr=1.1.*' \ 
  'r-forcats=1.0.*' \ 
  'r-ggforce=0.4.*' \
  'r-huxtable=5.5.*' \
  'r-purrr=1.0.*' \ 
  'r-readstata13=0.10.*' \
  'r-svyVGAM=1.*' \ 
  'r-srvyr=1.2.*' \ 
  'r-rpart=4.1.*' \ 
  'r-rpart.plot=3.1.*' \ 
  'r-caret=6.*' \
  'r-randomforest=4.7_1.*' \
  'r-cowplot=1.1.*' \ 
  'r-ggpubr=0.6.*' \
  'r-fastdummies=1.7.*' \
  'r-corrplot=0.*'\
  'r-haven=2.5.*' \
  'r-survey=4.*'\
  'r-ggplot2=3.5.*'\ 
  'r-tidyr=1.3.*' \
  'r-rodbc=1.*' \
  'r-readxl=1.4.*'\
  'r-reshape2=1.4.*' \
  'r-data.table=1.15.*' \ 
  'r-psych=2.4.*'  \
  'r-magrittr=2.0.*' \
  'r-stringr=1.5.*' \
  'r-foreign=0.*' \
  'r-config=0.3.*' \
  'r-rgeos=0.*' \
  'r-rgooglemaps=1.5.*' \
  'r-ggmap=4.0.*' \
  'r-ggthemes=5.1.*' \
  'r-maptools=1.*' \
  'r-plotly=4.*' \
  'r-raster=3.*' \
  'r-sf=1.*' \
  'r-stringi=1.*' &&\ 
  conda clean --all -y