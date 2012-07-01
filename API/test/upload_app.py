import os

from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename

import boto
from boto.s3.key import Key



UPLOAD_FOLDER = '/home/ivan/workspace/blibb-api/API/test/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'jpg', 'jpeg', 'gif', 'png'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS


def upload_to_s3(filename, key, bucket='dev.blibb'):
	c = boto.connect_s3()
	b = c.create_bucket(bucket)
	k = Key(b)
	k.key = key
	k.set_metadata('info_test', 'Imported from flask')
	k.set_contents_from_filename(app.config['UPLOAD_FOLDER'] + filename)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			upload_to_s3(filename, '872635583812872942893274293293')
			return 'File Uploaded! '

	return '''
		<html>
			<title>uploads</title>
			<body>
				<form action="" method="post" enctype="multipart/form-data">
					<input type="file" name="file" />
					<input type="submit" value="Upload" />
				</form>
			</body>
		</html>
	'''


if __name__ == '__main__':
    app.run(debug=True)