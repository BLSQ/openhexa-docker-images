import subprocess

# Delete work directory if any, and create tmp instead
subprocess.run(["rmdir", "/home/jovyan/work"])
subprocess.run(["mkdir", "/home/jovyan/tmp"])

# Make /home/jovyan read-only
subprocess.run(["chmod", "a-w", "/home/jovyan"])

# Make /home/jovyan/worskpace + /home/jovyan/tmp writable
subprocess.run(["chmod", "g+w", "/home/jovyan/workspace"])
subprocess.run(["chmod", "g+w", "/home/jovyan/tmp"])
