import os
from flask import Flask, request, redirect, url_for, render_template, flash, send_from_directory, Response
from werkzeug.utils import secure_filename
from midi2rdf import midi2rdf
from subprocess import Popen

UPLOAD_FOLDER = '/tmp/'
VIRTUOSO_LOAD = '/scratch/amp/midi/virtuoso-load/'
ALLOWED_EXTENSIONS = set(['mid', 'midi'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "asdklfjlakjsdhflkjh"

@app.route('/')
def hello_world():
    # dump = midi2rdf('/Users/Albert/src/midi2rdf/examples/ghostbusters.mid')
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part


        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            local_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(local_filename)
            dump = midi2rdf(local_filename, 'turtle')
            # If user accepts, we load the dump in the triplestore
            if request.form.get("cloud"):
                with open(VIRTUOSO_LOAD + filename + '.ttl', 'w') as rdffile:
                    rdffile.write(dump)
		Popen('/usr/local/virtuoso-opensource/bin/isql 1112 < /home/amp/src/midi2rdf-current/src/virtuoso-load.sql', shell=True)
            return Response(dump, mimetype="application/n-quads", headers={"Content-disposition": "attachment; filename={}".format(filename + '.ttl')})
            # return redirect(url_for('uploaded_file', filename=filename))
    return redirect('/')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8092, debug=True)
