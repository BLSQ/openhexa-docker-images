import subprocess

# Unmount GCS bucket of the workspace
subprocess.run(
    [
        "umount",
        "--lazy",  # the server's working directory is the mount
        "/home/jovyan/workspace",
    ]
)
subprocess.run(["rmdir", "/home/jovyan/workspace"])
