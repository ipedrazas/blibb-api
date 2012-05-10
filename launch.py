import subprocess
import sys

# some code here

pid = subprocess.Popen([sys.executable, "run.py"]) # call subprocess
pid = subprocess.Popen([sys.executable, "API/workers/server.py"]) # call subprocess