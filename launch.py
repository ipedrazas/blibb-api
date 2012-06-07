import subprocess
import sys

# some code here

pid = subprocess.Popen([sys.executable, "run.py"]) # call subprocess
pid2 = subprocess.Popen([sys.executable, "API/workers/server.py"]) # call subprocess
pid3 = subprocess.Popen([sys.executable, "API/workers/twitter_worker.py"]) # call subprocess