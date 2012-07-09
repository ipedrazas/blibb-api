import subprocess
import sys
import os

# some code here

os.putenv('DEV','yes')


pid = subprocess.Popen([sys.executable, "run.py"]) # call subprocess
pid2 = subprocess.Popen([sys.executable, "API/workers/server.py"]) # call subprocess
pid3 = subprocess.Popen([sys.executable, "API/workers/twitter_worker.py"]) # call subprocess