import subprocess
import sys

# some code here

pid = subprocess.Popen([sys.executable, "/home/ivan/workspace/blibb-api/run.py"]) # call subprocess
pid = subprocess.Popen([sys.executable, "/home/ivan/workspace/blibb-api/API/workers/server.py"]) # call subprocess
