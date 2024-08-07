import os

c = get_config()

# Iframe stuff
c.NotebookApp.tornado_settings = {
    "headers": {"Content-Security-Policy": os.environ["CONTENT_SECURITY_POLICY"]}
}

c.ServerApp.root_dir = "/home/jovyan/workspace"

# https://github.com/jupyter-server/jupyter-resource-usage
c.ResourceUseDisplay.track_cpu_percent = True
