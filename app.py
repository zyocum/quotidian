import os
import random
import tempfile
from flask import Flask, render_template, send_from_directory, request, jsonify, flash
from werkzeug import secure_filename
from extract_time_intervals import process_file, process_text
import logging
from logging.handlers import RotatingFileHandler
import shutil

# Configuration
SECRET_KEY = 'hin6bab8ge25*r=x&amp;+5$0kn=-#log$pt^#@vrqjld!^2ci@g*b'
DEBUG = True
dirname, filename = os.path.split(os.path.abspath(__file__))
UPLOAD_FOLDER = '{0}/media/audio'.format(os.path.abspath(dirname))
ALLOWED_EXTENSIONS = set(['wav', 'mp3'])

app = Flask(__name__)
app.config.from_object(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def home():
    # if uploading
    if request.method == 'POST':
        # get the audio file
        audio = request.files['audio_file']
        # if the audio is of an allowed filetype
        if audio and allowed_file(audio.filename):
            # secure the filename
            filename = secure_filename(audio.filename)
            temp_directory = tempfile.mkdtemp(dir=app.config['UPLOAD_FOLDER'])
            temp_folder = os.path.split(temp_directory)[1]
            full_path = os.path.join(temp_directory, filename)
            audio.save(full_path)
            # run speech comprehension audio file
            transcription, interval = process_file(full_path)
            # delete audio file
            for root, dirs, files in os.walk(os.path.split(temp_directory)[0], topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            # return guessed text
            app.logger.info(transcription + '\n' + interval)
            return jsonify(transcription=transcription, interval=interval)
    return render_template('home.html')

@app.route('/media/audio/<temp_directory>/<filename>')
def serve_temp_audio(temp_directory, filename):
    return send_from_directory(
                                os.path.join(app.config['UPLOAD_FOLDER'],
                                            temp_directory),
                                filename
                                )

@app.route('/media/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

							   
test_database = {}
							   
@app.route('/database', methods = ['POST'])
def database_request():
    transcription = request.form['transcription']
    date = request.form['date'].split(',')[0]
    transcription, interval = process_text(transcription)
    
    test_database[date] = interval

    app.logger.info(test_database)
    return jsonify(transcription=interval)
	
	
	
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port)