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
"notebook" | "singleuser")
  # Jupyternaut's file tools use the current working directory, so start in the
  # server root (/home/jovyan/workspace). Wait for the post-start hook to mount
  # the workspace bucket first so we don't cd into the underlying directory.
  if [[ -n $WORKSPACE_BUCKET_NAME && $WORKSPACE_STORAGE_ENGINE != local ]]; then
    timeout 60 bash -c 'until mountpoint -q /home/jovyan/workspace; do sleep 1; done' || echo "Workspace not mounted after 60s, starting anyway"
  fi
  mkdir -p /home/jovyan/workspace && cd /home/jovyan/workspace
  start-$command.sh $arguments
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
