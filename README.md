

# a) ACTIVATION

1. copy the git to local machine. enter quotidian folder.

2. create virtual environment (make sure virtualenv is installed)
    
    ```
        virtualenv venv
    ```
    
3. activate the virtual environment
    
    ```
        . venv/bin/activate
    ```

	windows:
	```
		venv\Scripts\activate
	```
    
4.  install dependencies
    
    ```
        pip install -r requirements.txt
    ```

	windows:
	```
		python -m pip install -r requirements.txt
	```

5. start app 
	
	```
	python app.py
	```

	
# b) USING APP

1. go to site:
	
	```
	localhost:5000
	```

	or 
	
	```
	http://127.0.0.1:5000/
	```

2. Speech to text

	a. hit the RECORD button
	
	b. click the ALLOW button on the Adobe Flash Player pop-up
	
	c. speak into your microphone about the amount of time you worked
	
	```
		speaker: "I worked from 9 to 5"
	```

	d. text box will fill with transcription of your audio if understood, will remain blank if failed


3. Text to timesheet
	
	a. use speech functionality to fill "I worked..." text box
	
	b. or, type transcription in "I worked..." text box
	
	c. hit SUBMIT button to update timesheet
	
	d. current day displayed on timesheet will update with times in text box


4. Changing days
	
	a. use the < button to scroll to previous days
	
	b. use the > button to scroll to future days
	

5. Timesheet editing
	
	a. you can click on any cell in the timesheet to toggle it from not-worked to worked and vice versa.
	
	
6. Clearing hours

	a. if there

	
# c) CREDENTIALS

1. no additional credentials are required


# d) LIMITATIONS

This application currently only supports on the hour start and end times

	currenlty supported: I worked from 9 to 5
	
	currenlty unsupported: I worked from 9:15 to 5:30

	
# e) TECH USED

1. Adobe Flash

2. Google Web Speech API
