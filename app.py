import csv
from prettytable import PrettyTable

_TASK_NAMES = {}
def config():
    global _TASK_NAMES
    
    _TASK_NAMES = {
        'Power of One': [0, powerOfOne],
        'One to Many': [1, oneToMany],
        'One Data Point': [2, oneDataPoint],
        'One Voice': [3, oneVoice],
        'One Idea': [4, oneIdea],
        'One to Return': [5, oneToReturn]
    }

def main():
    with open('survey.csv', 'rb') as infile:
        reader = csv.reader(infile)
        next(reader, None) # skip header
        
        for row in reader:
            taskName = row[1]

            for name in _TASK_NAMES:
                if name in taskName:
                    completed = _TASK_NAMES[name][1](row)
                    
                    if completed:
                        tallyTasks(name)
                    
                    internInfo(row[0], _TASK_NAMES[name][0], completed, row[7])
            
            campusTally(row)
    
    print "\n===================================="
    
    '''
    Print out results
    '''
    
    # Intern info
    header = ["Name", "Campus", "Tasks Completed"]
    x = PrettyTable(header)
    x.sortby = "Tasks Completed"
    x.reversesort = True
    x.padding_width = 1
    x.align = "l"
    
    outfile = open('output.csv', 'wb')
    writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(header)
    
    for name in _internInfo:
        row = [name, _internInfo[name][2], _internInfo[name][1]]
        
        # Write full table to CSV
        writer.writerow(row)
        
        # Only print interns that have completed all tasks
        if _internInfo[name][1] == len(_TASK_NAMES):
            x.add_row(row)
    
    outfile.close()
    
    print ""
    print "Interns that have completed all tasks.\nFull list of all interns and number of tasks completed is in output.csv"
    print x
    
    # Task Completion by Campus
    x = PrettyTable(["Campus", "# Submissions"])
    x.sortby = "# Submissions"
    x.reversesort = True
    x.padding_width = 1
    x.align = "l"
    
    for campus in _campuses:
        x.add_row([campus, _campuses[campus]])
    
    print ""
    print "Number of submissions by campus"
    print x
    
    # Task Completion Stats
    x = PrettyTable(["Task", "# Submissions"])
    x.sortby = "# Submissions"
    x.reversesort = True
    x.padding_width = 1
    x.align = "l"
    
    for task in _tasksCompletedByTask:
        x.add_row([task, _tasksCompletedByTask[task]])
    
    print ""
    print "Number of successfully completed submissions by task. (Includes duplicates)"
    print x
    
    # Volunteer stats
    print "Total expected hours volunteered: {0} ".format(_hoursVolunteered)
    print "Total alumni luncheon attendance: {0} ".format(_peopleLunchedWith)


_internInfo = {}
def internInfo(name, bit, taskCompleted, campus):
    '''
    Updates dictionary containing the following items:
        Key: Name
        Value:
        [
            Binary representation of tasks completed,
            Number of tasks completed,
            Campus
        ]
    
    param name: name of intern
    param bit: the bit that represents the task. See _TASK_NAMES for the bit values
    param taskCompleted: Boolean representing the status of the task for this person
    param campus: Name of campus this person works at
    '''
    if _internInfo.get(name) is None:
        _internInfo[name] = [0, 0, campus]
    
    if taskCompleted is True:
        _internInfo[name][0] = _internInfo[name][0] | 1 << bit
        _internInfo[name][1] = "{0:b}".format(_internInfo[name][0]).count("1")


_tasksCompletedByTask = {}
def tallyTasks(taskName):
    '''
    Keep track of how many submissions for each task
    
    param taskName: Name of task whose count should be incremented
    '''

    #taskName = next((name for name, attributes in _TASK_NAMES.items() if attributes[0] == bit), None)
    _tasksCompletedByTask[taskName] = _tasksCompletedByTask.get(taskName, 0) + 1

_campuses = {}
def campusTally(row):
    '''
    Tallies the number of responses from each campus and stores it into a dictionary
    
    param row: CSV row to read data from
    '''
    
    _campuses[row[7]] = _campuses.get(row[7], 0) + 1


_hoursVolunteered = 0
def powerOfOne(row):
    '''
    Tallies total hours volunteered by interns
    
    param row: CSV row to read data from
    return: True if person completed this task. False otherwise
    '''
    
    global _hoursVolunteered
    _hoursVolunteered = _hoursVolunteered + int(row[3])
    print "Intern: ", row[0], "\tTask: Volunteering", row[3], "hours"
    
    return row[2] == 'Yes'

_peopleLunchedWith = 0
def oneToMany(row):
    '''
    Tallies total number of people who attended alumni lunches
    
    param row: CSV row to read data from
    return: True
    '''
    global _peopleLunchedWith
    _peopleLunchedWith = _peopleLunchedWith + int(row[13])
    print "Intern: ", row[0], "\tTask: Lunch with", row[13], "people"
    
    return True

def oneDataPoint(row):
    '''
    Checks if person completed this task
    
    param row: CSV row to read data from
    return: True if person completed this task. False otherwise
    '''
    print "Intern: ", row[0], "\tTask: Survey"
    return row[6] == 'TRUE'

def oneVoice(row):
    '''
    Checks if person completed this task
    
    param row: CSV row to read data from
    return: True if person completed this task. False otherwise
    '''
    print "Intern: ", row[0], "\tTask: Video"
    
    return row[11] == 'Yes'

def oneIdea(row):
    '''
    Checks if person completed this task
    
    param row: CSV row to read data from
    return: True if person completed this task. False otherwise
    '''
    print "Intern: ", row[0], "\tTask: Spigit"
    return row[10] == 'TRUE' and row[14] == 'TRUE'

def oneToReturn(row):
    '''
    Checks if person completed this task
    
    param row: CSV row to read data from
    return: True if person completed this task. False otherwise
    '''
    print "Intern: ", row[0], "\tTask: External Profile"
    return row[4] == 'Yes'


config()
main()