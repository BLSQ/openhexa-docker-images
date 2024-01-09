FROM blsq/blsq/openhexa-base-environment

# For rgdal & sf (R)
RUN apt-get install -y libgdal-dev libudunits2-dev

# Python packages (mamba + conda-forge)
RUN mamba install --yes -c conda-forge \
  'lerc=4.*' \
  'dask-ml=2022.*' \
  'descartes=1.*' \
  'geoalchemy2=0.*' \
  'geopandas=0.*' \
  'hybridcontents=0.*' \
  'ipywidgets=7.*' \
  'lxml=4.*' \
  'mapclassify=2.*' \
  'nbresuse=0.*' \
  'netCDF4=1.*' \
  'pyarrow=11.0.0' \
  'rapidfuzz=2.*' \
  'rasterstats=0.*' \ 
  'rpy2=3.*' \
  'xarray=2022.*' \
  'zarr=2.*' \
  && mamba clean --yes --all

# Python packages (pip)
RUN pip install -U \
  'contextily==1.*' \
  'docxtpl==0.*' \
  'tabpy==2.*'
