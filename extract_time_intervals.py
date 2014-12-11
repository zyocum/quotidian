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
import datetime
import re

class TimeInterval():
    def __init__(self):
        self.now = datetime.datetime.now()
        self.start = datetime.datetime(self.now.year, self.now.month, self.now.day)
        self.end = self.now.replace(microsecond=0, second=0)
        self.duration = datetime.timedelta()

    def load_end(self, end_hour, end_minute = 0):        
        self.end = self.end.replace(hour = end_hour, minute = end_minute)

    def load_start(self, start_hour, start_minute = 0, calc_duration = False):
        self.start = self.start.replace(hour = start_hour, minute = start_minute)

    def load_duration(self, duration_hours, duration_mins):
        self.duration = datetime.timedelta(hours = duration_hours, 
                                           minutes = duration_mins)
   
    def calculate_duration(self):
        self.duration = self.end - self.start

    def calculate_start(self):
        self.start = self.end - self.duration

    def datetime_to_iso(self, datetime_obj):
        return "%d-%d-%dT%d:%d:%dZ" %(datetime_obj.year, 
                                      datetime_obj.month, 
                                      datetime_obj.day,
                                      datetime_obj.hour,
                                      datetime_obj.minute,
                                      datetime_obj.second)
    
    def interval_to_iso(self):
        start_string = self.datetime_to_iso(self.start)
        end_string = self.datetime_to_iso(self.end)
        return "%s/%s" %(start_string, end_string)
        
class GetTimeWorked():
    def __init__(self, transcription = ''):
        self.curr_interval = TimeInterval()
        # for testing
        self.transcription = transcription.lower()
        
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
        # parse transcription to get start and end times
        start_hour, start_minute = self.find_start_end(["from", "since"])
        end_hour, end_minute = self.find_start_end(["to", "till"])
        d_hours, d_minutes = self.find_duration()

        # logic to load start and end times        
        if start_hour:
            start_hour = int(start_hour[0])
            if start_minute:
                start_minute = int(start_minute[0])
                self.curr_interval.load_start(start_hour, start_minute)
            else:
                self.curr_interval.load_start(start_hour)
        if end_hour:
            end_hour = int(end_hour[0])
            # set am / pm for end time based on current time
            if start_hour > end_hour:
            #if self.curr_interval.now.hour > 12:
                end_hour = end_hour + 12
            if end_minute:
                end_minute = int(end_minute[0])
                self.curr_interval.load_end(end_hour, end_minute)
            else:
                self.curr_interval.load_end(end_hour)
        if d_hours and d_minutes:
            self.curr_interval.load_duration(int(d_hours[0]), int(d_minutes[0]))
        elif d_hours:
            self.curr_interval.load_duration(int(d_hours[0]), 0)             
        elif d_minutes:
            self.curr_interval.load_duration(0, int(d_minutes[0]))
            
        # calculate missing elements
        if not start_hour and not d_hours and not d_minutes:
            # if we need more information
            return "Error: need start time or duration worked"
        elif not d_hours and not d_minutes:
            self.curr_interval.calculate_duration()
        elif not start_hour:
            self.curr_interval.calculate_start()

def process_file(filepath):
    t = GetTimeWorked()
    audio =  sr.WavFile(filepath)
    t.speech_to_text(audio)
    error = t.parse_transcription()
    if error:
        return t.transcription, error
    else:
        return t.transcription, t.curr_interval.interval_to_iso()

def process_text(transcription):
    t = GetTimeWorked()
    t.transcription = transcription
    error = t.parse_transcription()
    if error:
        return t.transcription, error
    else:
        return t.transcription, t.curr_interval.interval_to_iso()

if __name__ == "__main__":
    
    # DEMO
    transcription = "I worked from 7 am to 8 pm" #"I've been working since 6 a.m."
 
#     t = GetTimeWorked(transcription)
#     t.parse_transcription()
#     print t.curr_interval.duration
#     print t.curr_interval.start
#     print t.curr_interval.end
#     print t.curr_interval.interval_to_iso()
    
    t = GetTimeWorked(transcription)
    print t.parse_transcription_new(transcription)
    
    #start: IN CD (N)
    #end: IN/TO CD (N)
    
    
#     print process_file("./test_5.wav")
    