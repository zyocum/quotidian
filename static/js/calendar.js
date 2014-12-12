// General functions
// Pad a number with leading zeros (or an arbitrary string)

function zip(source1, source2){
    var result=[];
    source1.forEach(function(o,i){
       result.push(o);
       result.push(source2[i]);
    });
    return result
}

function pad(n, width, z) {
  var z = z || '0';
  var n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

// Format an integer as HH:00
//function getHourString(number) {
//    return pad(number, 2) + ":00";
//}

function getHumanTimeString(dateTime) {
    var dt = dateTime.value.toLocaleTimeString().split(' '),
        hms = dt[0].split(':'),
        hm = hms.slice(0,2).join(':'),
        apm = dt[1];
    return [hm, apm].join(' ');
}

function toggleClass(element) {
    if (! element.classList.contains('worked')) {
        element.classList.add('worked');
    } else {
        element.classList.remove('worked');
    }
}

function isToggleable(element) {
    return ! element.classList.contains('noclick');
}

// Constants for time arithmetic
var millisecond = 1,
    second = 1000 * millisecond,
    minute = 60 * second,
    hour = 60 * minute,
    day = 24 * hour,
    week = 7 * day;

// A DateTime object that is a little more versatile than the built-in Date
function DateTime() {
    this.value = new Date();
    this.toString = function() {
        return this.value.toLocaleString();
    };
    this.toISOString = function() {
        return this.value.toISOString();
    }
    this.set = function(dt) {
        this.value.setTime(dt.getTime());
        return this;
    };
    this.year = function() {                 // [0000-9999]
        return this.value.getFullYear();
    };
    this.month = function() {                // [0-11]
        return this.value.getMonth();
    };
    this.day = function() {                  // [1-31]
        return this.value.getDate();
    };
    this.hour = function() {                 // [0-23]
        return this.value.getHours();
    };
    this.minute = function() {               // [0-59]
        return this.value.getMinutes();
    };
    this.second = function() {               // [0-59]
        return this.value.getSeconds();
    };
    this.millisecond = function() {           // [0-999]
        return this.value.getMilliseconds();
    };
    this.weekday = function() {              // [0-6]
        return this.value.getDay();
    };
    this.date = function() {                 // YYYY-MM-DD
        return [this.year(), this.month() + 1, this.day()].join('-');
    };
    this.weekdayName = function() {
        switch (this.value.getDay()) {
        case 0:
            return "Sunday";
            break;
        case 1:
            return "Monday"; 
            break;
        case 2:
            return "Tuesday";
            break;
        case 3:
            return "Wednesday";
            break;
        case 4:
            return "Thursday";
            break;
        case 5:
            return "Friday";
            break;
        case 6:
            return "Saturday";
            break;
        default:
            return;
        }
    }
    this.time = function() {                 // HH:MM:SS
        return [this.hour(), this.minute(), this.second()].join(':');
    }
    this.move = function(delta) {
        this.value.setTime(this.value.getTime() + delta);
        return this;
    };
    this.next = function(unit) {
        if (typeof(unit) !== 'undefined' && unit > 0) {
            this.move(unit);
        } else {
            this.move(+day);
        };
        return this;
    };
    this.previous = function(unit) {
        if (typeof(unit) !== 'undefined' && unit > 0) {
            this.move(-unit);
        } else {
            this.move(-day);
        };
        return this;
    };
}

// Return a DateTime that is midnight (12:00:00 AM) on the day of dateTime
// Default is 12:00:00 AM today
function getDayStart(dateTime) {
    var start = new DateTime();
    if (typeof(dateTime) !== 'undefined') {
        start.set(dateTime.value);
    };
    start.value.setHours(0);
    start.value.setMinutes(0);
    start.value.setSeconds(0);
    start.value.setMilliseconds(0);
    return start;
}

// Return a DateTime that is midnight (12:00:00 AM) on the first day of the 
// the week containing dateTime if specified
// Default is 12:00:00 AM on Sunday of this week
function getWeekStart(dateTime) {
    var start = new DateTime();
    if (typeof(dateTime) !== 'undefined') {
        start.set(dateTime.value);
    };
    while (start.weekday() !== 0) {
        start.previous();
    };
    return getDayStart(start);
}

// Create an array of 7 DateTimes [Sun,Mon,Tue,Wed,Thu,Fri,Sat]
// The week contains the given dateTime if specified
// Default is this week
function Week(dateTime) {
    var dt = new DateTime();
    if (typeof(dateTime) !== 'undefined'){
        dt.set(dateTime.value);
    };
    this.days = [getWeekStart(dt)];
    for (var i = 1; i < 7; i++) {
        this.days.push(getWeekStart(dt).next((i) * day));
    }
    this.toString = function() {
        return '[ ' + this.days.join(',\n  ') + ' ]';
    };
}

// Get a header label for the day and date
// E.g., "Sunday, November 30, 2014"
function dayHeaderLabel(dateTime) {
    var day = dateTime.weekdayName(),
        dateString = dateTime.value.toLocaleDateString();
    return [day, dateString].join(', ');
}

// Indicate the current hour row in the table if today is the current day
function setCurrentHourIndicator() {
    var currentHour = hours[now.hour()],
        currentHourLabel = trs[now.hour()+1].children[0];
    if (today.date() == new DateTime().date()) {
        currentHour.classList.add('currentHourCell');
        currentHourLabel.classList.add('currentHourLabel');
    } else {
        currentHour.classList.remove('currentHourCell');
        currentHourLabel.classList.remove('currentHourLabel');
    }
}

// Some convenient DateTime and other variables
var now = new DateTime(),
    today = getDayStart(now),
    tomorrow = getDayStart(new DateTime().next(day)),
    yesterday = getDayStart(new DateTime().previous(day)),
    nextHour = new DateTime().next(hour),
    lastHour = new DateTime().previous(hour),
    thisWeek = new Week(),
    nextWeek = new Week(new DateTime().next(week)),
    lastWeek = new Week(new DateTime().previous(week));

// Set up global DOM variables for easier accessibility
var calendar = document.getElementById('calendar'),
    table = document.createElement('table');
table.id = 'table';

// Make HTML table element and add it to the page
(function tableCreate() {
    var time = getDayStart(new DateTime());
    // Draw Table
    for(var i = 0; i < 25; i++){
        var tr = table.insertRow();
        for(var j = 0; j < 2; j++){
            var td = tr.insertCell();
            // Set header cell CSS class
            if (i == 0 || j == 0) {
                td.classList.add('noclick');
                td.classList.add('header');
            }
            // Add date in column header
            if ( i == 0 && j == 1) {
                td.classList.add('columnLabel');
                date = document.createTextNode(dayHeaderLabel(today));
                td.appendChild(date);
            }
            // Add hour labels
            if (i > 0 && j == 0) {
                td.classList.add('header');
                td.appendChild(
                    document.createTextNode(getHumanTimeString(time))
                );
            }
            // Add hour IDs
            if (i > 0 && j > 0) {
                td.id = 'Hour-' + (i-1);
            }
        }
        // Increment to the Next Hour
        time.next(hour);
    }
    
    // Setup onClick Events to Toggle Cell Color
    if(table) table.onclick = function(e) {
        var target = (e || window.event).target;
        if (target.tagName in {TD:1} && isToggleable(target)) {
            toggleClass(target);
            calendarClick();
        }
    };
    
    // Append the table to the calendar div
    calendar.appendChild(table);
    
    // Provide easy access to the table rows (trs) and table cells (hours)
    trs = table.firstElementChild.children;
    hours = [];
    for (var i = 1; i < trs.length; i++) {
        hours.push(trs[i].children[1]);
    }
    
    // Indicate current hour
    setCurrentHourIndicator();
})();

// Set today's date to the next day
nextDay = function() {
    today.next(day);
    date.nodeValue = dayHeaderLabel(today);
    setCurrentHourIndicator();
}

// Set today's date to the previous day
previousDay = function() {
    today.previous(day);
    date.nodeValue = dayHeaderLabel(today);
    setCurrentHourIndicator();
}

setHours = function(start, end) {
    hours.slice(start, end).map(function(hour) {
        if (! hour.classList.contains('worked')) {
            hour.classList.add('worked');
        }
    });
}

unsetHours = function(start, end) {
    hours.slice(start, end).map(function(hour) {
        if (hour.classList.contains('worked')) {
            hour.classList.remove('worked');
        }
    });
}

// Set hours in the interval (specified in the HTML form hidden value) as worked
fillHours = function() {
    var intervals = document.querySelector('input[type="hidden"]').value;
    for (var i = 0; i < intervals.length; i++) {
        var interval = intervals[i],
            start = startHour(interval),
            end = endHour(interval);
        setHours(start, end);
    }
}

startHour = function(interval) {
    return parseInt(interval.split('-')[0].split('T')[1].split(':')[0])-1;
}

endHour = function(interval) {
    return parseInt(interval.split('-')[1].split('T')[1].split(':')[0])-1;
}

// Set all hours as not worked
unfillAllHours = function() {
    unsetHours(0, 24);
}

// Return whether the given hour was worked or not
worked = function(hour) {
    return (hour.classList.contains('worked'));
}

// Return an array of the table cell elements that are classified as worked
getWorkedHours = function() {
    return hours.filter(worked);
}

// Return whether the given hour is the start of an interval of worked hours
isStartOfInterval = function(hour) {
    var i = hours.indexOf(hour);
    if (0 <= i && i < hours.length) {
        return (i > 0) ? (worked(hours[i]) && (! worked(hours[i-1]))) : worked(hours[i]);
    }
}

// Return whether the given hour is the end of an interval of worked hours
isEndOfInterval = function(hour) {
    var i = hours.indexOf(hour);
    if (0 <= i && i+1 < hours.length) {
        return (i+1 < hours.length) ? (worked(hours[i]) && (! worked(hours[i+1]))) : worked(hours[i]);
    }
}

// Return an array of ISO interval strings corresponding to the intervals
// that are currently set as worked
getIntervals = function() {
    var starts = hours.filter(isStartOfInterval),
        ends = hours.filter(isEndOfInterval)
        intervals = [];
    for (var i = 0; i < starts.length; i++) {
        var d1 = new Date(today.value.toDateString()),
            d2 = new Date(today.value.toDateString()),
            interval = [];
        d1.setHours(hours.indexOf(starts[i]));
        d2.setHours(hours.indexOf(ends[i])+1);
        interval.push(d1.toISOString());
        interval.push(d2.toISOString());
        console.log('Interval ' + i + ' : ' + interval.join('/'));
        intervals.push(interval.join('/'));
    }
    return intervals.join(",");
}

// CALL THIS WHEN YOU SUBMIT TIME
function pushTime() {
    var req = new XMLHttpRequest()
    req.onreadystatechange = function()
    {
        if (req.readyState == 4)
        {
            if (req.status != 200)
            {
                //error handling code here
            }
            else
            {
                //get request - data returned by app.py
                var response = JSON.parse(req.responseText),
                    intervals = response.intervals.split(',');
                //document.getElementById('myDiv').innerHTML = response.interval //display get
                // HOOK INTO CALENDAR GUI HERE
                for (var i = 0; i < intervals.length; i++) {
                    var start = startHour(intervals[i]),
                        end = endHour(intervals[i]);
                    setHours(start, end);
                }
            }
        }
    }
    //post reqest - data sent to app.py
    req.open('POST', '/push_time');
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    var transcription = document.getElementById('user_text').value;
    var postVars = 'transcription='+transcription+'&date='+today.toISOString();
    req.send(postVars);
    return false;
}

// CALL THIS WHEN YOU CHANGE DAY
function pullTime() {
    var req = new XMLHttpRequest()
    req.onreadystatechange = function()
    {
        if (req.readyState == 4)
        {
            if (req.status != 200)
            {
                //error handling code here
            }
            else
            {
                //get request - data returned by app.py
                var response = JSON.parse(req.responseText),
                    intervals = response.intervals.split(',');
                //document.getElementById('myDiv').innerHTML = response.interval //display get
                // HOOK INTO CALENDAR GUI HERE
                for (var i = 0; i < intervals.length; i++) {
                    var start = startHour(intervals[i]),
                        end = endHour(intervals[i]);
                    setHours(start, end);
                }
            }
        }
    }
    //post reqest - data sent to app.py
    req.open('POST', '/pull_time');
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    var postVars = 'date='+today.toISOString();
    req.send(postVars);
    return false;
}

// CALL THIS WHEN YOU CLEAR DAY
function clearTime() {
    var req = new XMLHttpRequest()
    req.onreadystatechange = function()
    {
        if (req.readyState == 4)
        {
            if (req.status != 200)
            {
                //error handling code here
            }
            else
            {
                //get request - data returned by app.py
                var response = JSON.parse(req.responseText)
                //document.getElementById('myDiv').innerHTML = response.interval //display get
            }
        }
    }
    //post reqest - data sent to app.py
    req.open('POST', '/clear_time');
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    var postVars = 'date='+today.toISOString();
    req.send(postVars);
    return false;
}

function calendarClick() {
    var req = new XMLHttpRequest()
    //req.onreadystatechange = function()
    //{
    //    if (req.readyState == 4)
    //    {
    //        if (req.status != 200)
    //        {
    //            //error handling code here
    //        }
    //        else
    //        {
    //            //post request
    //        }
    //    }
    //}
    //post reqest - data sent to app.py
    req.open('POST', '/calendar_click');
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    var postVars = 'intervals='+getIntervals()+'&date='+today.toISOString();
    req.send(postVars);
    return false;
}

function save() {
    var req = new XMLHttpRequest()
    req.onreadystatechange = function()
    {
        if (req.readyState == 4)
        {
            if (req.status != 200)
            {
                //error handling code here
            }
            else
            {
                //get request
                var response = JSON.parse(req.responseText),
                    csv = response.csv,
                    csvData = 'data:application/csv;charset=utf-8,' + encodeURIComponent(response.csv);
                console.log(csv)
                $(this).attr({
                    'download' : 'timesheet.csv',
                    'href' : csvData,
                    'target' : '_blank'
                });
            }
        }
    }
    req.open('POST', '/save');
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    var postVars = 'date='+today.toISOString();
    req.send(postVars);
    return false;
    
}