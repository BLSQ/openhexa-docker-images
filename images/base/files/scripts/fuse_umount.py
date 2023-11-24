import subprocess

# Unmount GCS bucket of the workspace
subprocess.run(
    [
        "umount",
        "/home/jovyan/workspace",
    ]
)
subprocess.run(["rmdir", "/home/jovyan/workspace"])
