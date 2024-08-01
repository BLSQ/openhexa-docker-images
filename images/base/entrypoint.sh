#!/bin/bash
set -e

command=$1
arguments=${*:2}
if [[ -z $arguments ]]; then
  arguments_debug="no arguments"
else
  arguments_debug="arguments ($arguments)"
fi

# echo "Running \"$command\" with $arguments_debug"

show_help() {
  echo """
  Available commands:

  notebook            : start notebook server
  pipeline            : run pipeline in local or cloud mode (ex: pipeline cloudrun '{}')
  
  Any arguments passed will be forwarded to the executed command
  """
}

case "$command" in
"notebook")
  start-notebook.sh --ServerApp.root_dir=/home/jovyan/workspace
  ;;
"singleuser")
  start-singleuser.sh
  ;;
"pipeline")
  if [[ "$REMOTE_DEBUGGER" == "true" ]]; then
    echo "Starting pipeline with debugpy on port 5678..."
    python -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:5678 --wait-for-client /home/hexa/.hexa_scripts/bootstrap_pipeline.py $arguments
  else
    python /home/hexa/.hexa_scripts/bootstrap_pipeline.py $arguments
  fi
  ;;
"help")
  show_help
  ;;
esac
