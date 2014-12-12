'''
Created on Nov 6, 2014

@author: Aaron Levine
@email: aclevine@brandeis.edu

speech_recognition docs:
https://pypi.python.org/pypi/SpeechRecognition/
https://github.com/Uberi/speech_recognition

ISO for time encoding:
http://en.wikipedia.org/wiki/ISO_8601
'''
import speech_recognition as sr
import re
from datetime import datetime, timedelta

spelling_to_int =  {'one': 1,
                    'two': 2,
                    'three': 3,
                    'four': 4,
                    'five': 5,
                    'six': 6,
                    'seven': 7,
                    'eight': 8,
                    'nine': 9,
                    'ten': 10,
                    'eleven': 11,
                    'twelve': 12,
                    'thirteen': 13,
                    'fourteen': 14,
                    'fifteen': 15,
                    'sixteen': 16,
                    'seventeen': 17,
                    'eighteen': 18,
                    'nineteen': 19,
                    'twenty': 20,
                    'thirty': 30,
                    'forty': 40,
                    'fifty': 50}

time_terms =  set(list(spelling_to_int.keys()) + [str(num) for num in spelling_to_int.values()])


class TimeInterval():
    def __init__(self, date=''):
        self.now = datetime.datetime.now()
        if date:
            year, month, day = map(int, date.split("-"))
            self.start = datetime.datetime(year, month, day)
        else:
            self.start = datetime.datetime(self.now.year, self.now.month, self.now.day)
        self.end = self.now.replace(microsecond=0, second=0)
        self.duration = timedelta()

    def load_end(self, end_hour, end_minute = 0):        
        self.end = self.end.replace(hour = end_hour, minute = end_minute)

    def load_start(self, start_hour, start_minute = 0, calc_duration = False):
        self.start = self.start.replace(hour = start_hour, minute = start_minute)

    def load_duration(self, duration_hours, duration_mins):
        self.duration = timedelta(hours = duration_hours, 
                                           minutes = duration_mins)
   
    def calculate_duration(self):
        self.duration = self.end - self.start

    def calculate_start(self):
        self.start = self.end - self.duration

    #def datetime_to_iso(self, datetime_obj):
    #    return "%d-%d-%dT%d:%d:%dZ" %(datetime_obj.year, 
    #                                  datetime_obj.month, 
    #                                  datetime_obj.day,
    #                                  datetime_obj.hour,
    #                                  datetime_obj.minute,
    #                                  datetime_obj.second)
    
    def interval_to_iso(self):
        #start_string = self.datetime_to_iso(self.start)
        #end_string = self.datetime_to_iso(self.end)
        return "{}/{}".format(self.start.isoformat(), self.end.isoformat())
        
class GetTimeWorked():
    def __init__(self, transcription = '', date=''):
        # for testing
        self.transcription = transcription.lower()
        self.curr_interval = TimeInterval(date)        
        
    def speech_to_text(self, input_stream):
        r = sr.Recognizer()
        with input_stream as source:
            audio = r.record(source)
        try:
            self.transcription = r.recognize(audio)
            return self.transcription
        except LookupError:
            return "Could not understand audio"

    def find_start_end(self, flag_list):
        hour_p = "\d{1,2}"
        minute_p = ":(\d\d)"
        hour = []
        minute = []
        for flag in flag_list:
            if not hour:
                hour = re.findall("%s (%s)" %(flag, hour_p), self.transcription)
            if not minute:
                minute = re.findall("%s %s%s" %(flag, hour_p, minute_p), self.transcription)
        return hour, minute
        
    def find_duration(self):
        d_hours = re.findall("(\d+) hour", self.transcription)
        d_minutes = re.findall("(\d+) minute", self.transcription)
        return d_hours, d_minutes

    def parse_transcription(self):
        tokens = self.transcription.split()
        print tokens
        time_count = len([tok for tok in tokens if tok in time_terms])
        
        # no times provided 
        if time_count == 0:
            return "Error: need start time or duration worked"
        
        # duration provided
        if 'for' in tokens:
            d_hours = re.findall("(\d+) hour", self.transcription)
            d_minutes = re.findall("(\d+) minute", self.transcription)
            if d_hours and d_minutes:
                self.curr_interval.load_duration(int(d_hours[0]), int(d_minutes[0]))
            elif d_hours:
                self.curr_interval.load_duration(int(d_hours[0]), 0)
            elif d_minutes:
                self.curr_interval.load_duration(0, int(d_minutes[0]))
            self.curr_interval.calculate_start()
            return self.curr_interval.interval_to_iso()
        # start / end provided
        intervals = []
        if time_count == 1:
            for i in range(len(tokens)):            
                tok = tokens[i]
                if tok in time_terms:
                    if tok in spelling_to_int:
                        hour = spelling_to_int[tok]
                    else:
                        hour = int(tok)
                    self.curr_interval.load_start(hour)
                    return self.curr_interval.interval_to_iso()
        if time_count % 2 == 0:
            is_start = True
            last = 0
            for i in range(len(tokens)):            
                tok = tokens[i]
                if tok in time_terms:
                    if tok in spelling_to_int:
                        hour = spelling_to_int[tok]
                    else:
                        hour = int(tok)
                    if last >= hour:
                        hour += 12
                    else:
                        for tok in tokens[i+1:i+2]:
                            if tok == 'pm' and hour <= 12:
                                hour += 12
                                break
                    if is_start:
                        self.curr_interval.load_start(hour)
                        is_start = False
                    else:
                        self.curr_interval.load_end(hour)                    
                        intervals.append(self.curr_interval.interval_to_iso())
                        is_start = True
                    last = hour
            return ','.join(intervals)


def process_file(filepath):
    t = GetTimeWorked()
    audio =  sr.WavFile(filepath)
    t.speech_to_text(audio)
    intervals = t.parse_transcription()
    return t.transcription, intervals

def process_text(transcription, date):
    t = GetTimeWorked(date)
    t.transcription = transcription
    intervals = t.parse_transcription()
    return t.transcription, intervals

