import subprocess

# Rename work to tmp
subprocess.run(["mv", "/home/jovyan/work", "/home/jovyan/tmp"])

# # Make /home/jovyan read-only
# subprocess.run(["chmod", "a-w", "/home/jovyan"])

# Make /home/jovyan/worskpace + /home/jovyan/tmp writable
subprocess.run(["chmod", "g+w", "/home/jovyan/tmp"])
