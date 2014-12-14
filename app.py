import os
import tempfile
from flask import Flask, render_template, send_from_directory, request, jsonify, flash, make_response
from werkzeug import secure_filename
from extract_time_intervals import process_file, process_text
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta, date
import shutil

# Configuration
SECRET_KEY = 'hin6bab8ge25*r=x&amp;+5$0kn=-#log$pt^#@vrqjld!^2ci@g*b'
DEBUG = True
dirname, filename = os.path.split(os.path.abspath(__file__))
UPLOAD_FOLDER = '{0}/media/audio'.format(os.path.abspath(dirname))
ALLOWED_EXTENSIONS = set(['wav', 'mp3'])

app = Flask(__name__)
app.config.from_object(__name__)
test_database = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

class Week(object):
    """A week """
    def __init__(self, dt=datetime.now()):
        super(Week, self).__init__()
        self.start = self.get_start(dt)
        self.dates = self.get_dates()
        self.days = self.get_days()
    
    def __getitem__(self, day):
        if isinstance(day, basestring):
            index = {
                'mon' : 0,
                'tue' : 1,
                'wed' : 2,
                'thu' : 3,
                'fri' : 4,
                'sat' : 5,
                'sun' : 6
            }
            return self.dates[index[day.lower()[:3]]]
        else:
            return self.dates[day]
    
    def __iter__(self):
        return iter(self.dates)
    
    def __repr__(self):
        return repr(self.days)
    
    def __len__(self):
        return len(self.days)
    
    def get_start(self, dt):
        """docstring for get_start"""
        d = dt.date()
        while not (d.weekday() == 0):
            d -= timedelta(hours=24)
        return d
    
    def get_dates(self):
        """docstring for get_days"""
        return [self.start + timedelta(hours=i*24) for i in range(7)]
    
    def get_days(self):
        return map(date.isoformat, self.dates)
    
    def intervals(self):
        return [test_database.get(day, '') for day in self.get_days()]
    
    def dt_intervals(self):
        intervals = []
        for interval in self.intervals():
            if any(interval):
                intervals.append([map(get_datetime, iv.split('/')) for iv in interval.split(',')])
            else:
                intervals.append([])
        return intervals
    
    def hr_intervals(self, time_format='%I:%M %p'):
        intervals = []
        for interval in self.dt_intervals():
            output = []
            if any(interval):
                for start, end in interval:
                    output.append(
                        ' to '.join([
                            start.strftime(time_format),
                            end.strftime(time_format)
                        ])
                    )
            intervals.append(','.join(output))
        return intervals
    
    def hr_dates(self, date_format='%m/%d/%Y'):
        return [dt.strftime(date_format) for dt in self.get_dates()]
    
    def hour_durations(self):
        intervals = []
        for interval in self.dt_intervals():
            if any(interval):
                intervals.append([
                    end.hour - start.hour for start, end in interval
                ])
            else:
                intervals.append([])
        return intervals
    
    def hour_totals(self):
        return map(sum, self.hour_durations())

    def total_hours(self):
        return sum(self.hour_totals())

def get_datetime(iso_date_string):
    """Return a datetime object for the given an ISO formatted date string."""
    print "iso_date_string:", iso_date_string
    if iso_date_string:
        app.logger.info(iso_date_string)
        date, time = iso_date_string.split('T')
        year, month, day = date.split('-')
        hour, minute, second = time.split(':')
        if '.' in second:
            second, _ = second.split('.')
        args = map(int, (year, month, day, hour, minute, second))
        return datetime(*args)
    else:
        return ''

def csv(week):
    """Take a week's worth of intervals and return a timesheet as CSV."""
    days = (
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'
    )
    dates = week.hr_dates()
    intervals = week.hr_intervals()
    hours = week.hour_totals()
    total = week.total_hours()
    csv = ',Date,Daily Total Hours,\n'
    for i in range(7):
        csv += '{day},{date},{total},{intervals}\n'.format(
            day=days[i],
            date=dates[i],
            intervals=intervals[i],
            total=hours[i]
        )
    csv += '\n,Total Weekly Hours,{total}'.format(total=total)
    return csv

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

@app.route('/push_time', methods = ['POST'])
def push_time():
    transcription = request.form['transcription']
    dt = request.form['date'].split('T')[0]
    transcription, interval = process_text(transcription, dt)
    
    temp = test_database.get(dt, '')
    if temp == '':
        test_database[dt] = interval
    else:
        test_database[dt] =  temp + ',' + interval
    
    intervals = test_database[dt]
    app.logger.info(intervals)
    return jsonify(intervals=intervals)
    
@app.route('/pull_time', methods = ['POST'])
def pull_time():
    dt = request.form['date'].split('T')[0]

    intervals = test_database.get(dt, '')

    app.logger.info(test_database)
    return jsonify(intervals=intervals)

@app.route('/clear_time', methods = ['POST'])
def clear_time():
    dt = request.form['date'].split('T')[0]

    test_database[dt] = ''

    app.logger.info(test_database)
    return jsonify(intervals='')
    
@app.route('/calendar_click', methods = ['POST'])
def calendar_click():
    dt = request.form['date'].split('T')[0]
    intervals = request.form['intervals']

    test_database[dt] = intervals

    app.logger.info(test_database)
    return jsonify(intervals='')

@app.route('/save', methods = ['POST'])
def save():
    """This route will return a response with the csv data."""
    dt = request.form['date'].split('T')[0]
    year, month, day = map(int, dt.split('-'))
    date_time = datetime(year, month, day)
    timesheet = csv(Week(date_time))
    app.logger.info('CSV : {}'.format(timesheet))
    return jsonify(csv=timesheet)
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port)