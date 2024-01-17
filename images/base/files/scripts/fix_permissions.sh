#!/bin/bash

# Move /home/jovyan/work to /home/jovyan/tmp
mv /home/jovyan/work /home/jovyan/tmp

# Remove all write rights on /home/jovyan
chmod gu-w /home/jovyan

# Give write rights to the group on /home/jovyan/workspace
chmod -R g+w /home/jovyan/workspace
chmod -R g+w /home/jovyan/tmp
