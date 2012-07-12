
from API import app


import os

# some code here
os.putenv('DEV', 'yes')

app.run(debug= True)
