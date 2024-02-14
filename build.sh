cd images/base 
sudo docker build . -t blsq/openhexa-base-environment:latest
cd ..
cd ..

cd images/legacy
sudo docker build . -t blsq/openhexa-legacy-environment:latest
cd ..
cd ..

cd images/blsq
sudo docker build . -t blsq/openhexa-blsq-environment:latest                       
cd ..
cd ..
