# We import the markdown library
import markdown
from flask import Flask
from flask import render_template
from flask import Markup

app = Flask(__name__)
@app.route('/')

def index():
  content = """
Chapter
=======

Section
-------

* Item 1
* Item 2
"""
  content = Markup(markdown.markdown(content))
  return render_template('index.html', **locals())

app.run(host='0.0.0.0', port=88, debug=True)
