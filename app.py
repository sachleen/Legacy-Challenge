import sqlite3 as sql
import csv
from prettytable import PrettyTable
import datetime
import sys

'''
Configuration
'''

# Readable names for CSV column numbers
_CSV_COLUMNS = {
    'name': 0,
    'task_name': 1,
    'campus': 7,
    
    # Impact
    'impact_min_hours': 2,      # required
    'impact_share_pic': 18,     # required
    'impact_total_hours': 3,    # stats only
    
    #Connect
    'connect_share_pic': 17,        # required
    'connect_number_attended': 13,  # stats only
    'connect_university': 8,        # stats only
    
    #Improve
    'improve_did_survey': 6,    # required
    
    #InternView
    'internview_did_video': 11, # required
    
    #Innovate
    'innovate_submit_idea': 14,     # required
    'innovate_meets_net_worth': 10, # required
    
    #Return
    'return_did_profile': 4,    # required
    'return_did_resume': 16     # required
}

# Match the task with the column names
_TASK_NAMES = (
    'Impact',
    'Connect',
    'Improve',
    'InternView',
    'Innovate',
    'Return'
)

_DB_FILE = 'legacy.db'

def main():
    if len(sys.argv) < 2:
        print "Must specify input file name"
        exitFunc()
    
    global _CSV_FILE
    _CSV_FILE = sys.argv[1]#'survey.csv'

    print "Setting up database"
    initDatabase()
    print "Importing survey into database"
    csv2sql()
    print "Done!"

    
    '''
    Run Reports
    '''

    
    '''
    Number of successful completions for each task
    ============================================================
    '''
    # Query Database
    con = sql.connect(_DB_FILE)
    cur = con.cursor()
    cur.execute("""
    SELECT 
        sum(case when impact = 'Y' then 1 else 0 end) impact_cnt,
        sum(case when connect = 'Y' then 1 else 0 end) connect_cnt,
        sum(case when improve = 'Y' then 1 else 0 end) improve_cnt,
        sum(case when internview = 'Y' then 1 else 0 end) internview_cnt,
        sum(case when innovate = 'Y' then 1 else 0 end) innovate_cnt,
        sum(case when return = 'Y' then 1 else 0 end) return_cnt
    FROM results;
    """)
    counts = cur.fetchone()
    con.close()
    
    # Output Result
    x = PrettyTable(["Task", "# Completed"])
    x.sortby = "# Completed"
    x.reversesort = True
    x.padding_width = 1
    x.align = "l"
    
    for idx, task in enumerate(_TASK_NAMES):
        x.add_row([task, counts[idx]])
    
    print ""
    print "Most popular tasks"
    print x

    
    '''
    Most active campuses
    ============================================================
    '''
    # Query Database
    con = sql.connect(_DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT campus, count(*) as interns FROM results GROUP BY campus;")
    results = cur.fetchall()
    con.close()
    
    # Output Result
    x = PrettyTable(("Campus", "# Interns"))
    x.sortby = "# Interns"
    x.reversesort = True
    x.padding_width = 1
    x.align = "l"

    for row in results:
        x.add_row(row)
    
    print ""
    print "Most active campuses"
    print x
    
    
    print ""
    print "Other stats"
    '''
    Total volunteer hours
    ============================================================
    '''
    # Query Database
    con = sql.connect(_DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT count(*) as numResponses, sum(impact_total_hours) as total FROM results WHERE impact = 'Y';")
    results = cur.fetchone()
    con.close()
    
    # Output Result
    print "{0} interns have volunteered a total of {1} hours".format(*results)
    
    '''
    Total people at lunch
    ============================================================
    '''
    # Query Database
    con = sql.connect(_DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT count(*) as numResponses, sum(connect_number_attended) as total FROM results WHERE connect = 'Y';")
    results = cur.fetchone()
    con.close()
    
    # Output Result
    print "{0} interns had lunch with {1} people form their universities".format(*results)
    
        
    '''
    Interns and number of tasks they've completed
    ============================================================
    '''
    # Query Database
    con = sql.connect(_DB_FILE)
    cur = con.cursor()
    cur.execute("""
    SELECT name, campus,
    (
        (case when impact == 'Y' then 1 else 0 end) +
        (case when connect == 'Y' then 1 else 0 end) +
        (case when improve = 'Y' then 1 else 0 end) +
        (case when internview = 'Y' then 1 else 0 end) +
        (case when innovate = 'Y' then 1 else 0 end) +
        (case when return = 'Y' then 1 else 0 end)
    ) as tasks_completed
    FROM results
    ORDER BY tasks_completed DESC, name ASC
    """)
    results = cur.fetchall()
    con.close()
    
    # Output Result
    fileName = 'allInterns_%s.csv' % (datetime.date.today())
    outfile = open(fileName, 'wb')
    writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(("Name", "Campus", "# Completed"))
    
    for row in results:
        writer.writerow(row)
    
    print ""
    print "Full list of all interns and number of tasks completed is in allInterns.csv"
    
    '''
    Updates since last time script was run
    ============================================================
    '''
    # Query Database
    con = sql.connect(_DB_FILE)
    cur = con.cursor()
    cur.execute("""
    SELECT name, campus, updateCnt
    FROM results
    WHERE updateCnt > 0
    ORDER BY updateCnt DESC, name ASC
    """)
    results = cur.fetchall()
    con.close()
    
    # Output Result
    fileName = 'changesOnly_%s.csv' % (datetime.date.today())
    outfile = open(fileName, 'wb')
    writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(("Name", "Campus", "# Completed"))
    
    for row in results:
        writer.writerow(row)
    
    print ""
    print "Added new submissions from last time script was run to newEntries.csv"
    


def initDatabase():
    '''
    Setup the SQLite database. Creates table for results if it doesn't already exist and clears updateCnt.
    '''
    con = sql.connect(_DB_FILE)
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS `results` (
                    `name` TEXT NOT NULL UNIQUE,
                    `campus` TEXT,
                    `impact` TEXT,
                    `impact_total_hours` INT,
                    `connect` TEXT,
                    `connect_number_attended` INT,
                    `connect_university` TEXT,
                    `improve` TEXT,
                    `internview` TEXT,
                    `innovate` TEXT,
                    `return` TEXT,
                    `updateCnt` INT
                );""")
    cur.execute("UPDATE results SET updateCnt = 0;")
    con.commit()
    con.close()

def csv2sql():
    '''
    Imports _CSV_FILE data into _DB_FILE with column relationship represented in _CSV_COLUMNS
    '''
    try:
        infile = open(_CSV_FILE, 'rb')
    except IOError:
        print "Input file not found."
        exitFunc()
    
    reader = csv.reader(infile)
    next(reader, None) # skip header
    
    con = sql.connect(_DB_FILE)
    cur = con.cursor()
    
    for row in reader:
        # Progress indicator
        pos = reader.line_num % 20
        
        print '\r[',
        print ' '*(pos),
        print '=',
        print ' '*(19-pos),
        print ']',
        
        # Try an insert
        if (
                (isSet(row[_CSV_COLUMNS['impact_min_hours']]) and isSet(row[_CSV_COLUMNS['impact_share_pic']]))
                or isSet(row[_CSV_COLUMNS['connect_share_pic']])
                or isSet(row[_CSV_COLUMNS['improve_did_survey']])
                or isSet(row[_CSV_COLUMNS['internview_did_video']])
                or (isSet(row[_CSV_COLUMNS['innovate_submit_idea']]) and isSet(row[_CSV_COLUMNS['innovate_meets_net_worth']]))
                or (isSet(row[_CSV_COLUMNS['return_did_profile']]) and isSet(row[_CSV_COLUMNS['return_did_resume']]))
            ):
            cur.execute("INSERT OR IGNORE INTO results VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                row[_CSV_COLUMNS['name']],
                row[_CSV_COLUMNS['campus']],
                'Y' if isSet(row[_CSV_COLUMNS['impact_min_hours']]) and isSet(row[_CSV_COLUMNS['impact_share_pic']]) else 'N',
                row[_CSV_COLUMNS['impact_total_hours']],
                'Y' if isSet(row[_CSV_COLUMNS['connect_share_pic']]) else 'N',
                row[_CSV_COLUMNS['connect_number_attended']],
                row[_CSV_COLUMNS['connect_university']],
                'Y' if isSet(row[_CSV_COLUMNS['improve_did_survey']]) else 'N',
                'Y' if isSet(row[_CSV_COLUMNS['internview_did_video']]) else 'N',
                'Y' if isSet(row[_CSV_COLUMNS['innovate_submit_idea']]) and isSet(row[_CSV_COLUMNS['innovate_meets_net_worth']]) else 'N',
                'Y' if isSet(row[_CSV_COLUMNS['return_did_profile']]) and isSet(row[_CSV_COLUMNS['return_did_resume']]) else 'N',
                1
            ))
            rowsAffected = cur.rowcount
            con.commit()
        
        if rowsAffected == 0:
            # Insert failed because record already exists, update it
            
            if _TASK_NAMES[0] in row[_CSV_COLUMNS['task_name']]:
                # Impact
                if isSet(row[_CSV_COLUMNS['impact_min_hours']]) and isSet(row[_CSV_COLUMNS['impact_share_pic']]):
                    cur.execute('UPDATE results SET impact = \'Y\', impact_total_hours = ?, updateCnt = updateCnt + 1 WHERE name = ? and impact = \'N\'', (
                        row[_CSV_COLUMNS['impact_total_hours']],
                        row[_CSV_COLUMNS['name']]
                    ))
                
            elif _TASK_NAMES[1] in row[_CSV_COLUMNS['task_name']]:
                # Connect
                if isSet(row[_CSV_COLUMNS['connect_share_pic']]):
                    cur.execute('UPDATE results SET connect = \'Y\', connect_number_attended = ?, connect_university = ?, updateCnt = updateCnt + 1 WHERE name = ? and connect = \'N\'', (
                        row[_CSV_COLUMNS['connect_number_attended']],
                        row[_CSV_COLUMNS['connect_university']],
                        row[_CSV_COLUMNS['name']]
                    ))
                
            elif _TASK_NAMES[2] in row[_CSV_COLUMNS['task_name']]:
                # Improve
                if isSet(row[_CSV_COLUMNS['improve_did_survey']]):
                    cur.execute('UPDATE results SET improve = \'Y\', updateCnt = updateCnt + 1 WHERE name = ? and improve = \'N\'', (
                        row[_CSV_COLUMNS['name']],
                    ))
                
            elif _TASK_NAMES[3] in row[_CSV_COLUMNS['task_name']]:
                # InternView
                if isSet(row[_CSV_COLUMNS['internview_did_video']]):
                    cur.execute('UPDATE results SET internview = \'Y\', updateCnt = updateCnt + 1 WHERE name = ? and internview = \'N\'', (
                        row[_CSV_COLUMNS['name']],
                    ))
                
            elif _TASK_NAMES[4] in row[_CSV_COLUMNS['task_name']]:
                # Innovate
                if isSet(row[_CSV_COLUMNS['innovate_submit_idea']]) and isSet(row[_CSV_COLUMNS['innovate_meets_net_worth']]):
                    cur.execute('UPDATE results SET innovate = \'Y\', updateCnt = updateCnt + 1 WHERE name = ? and innovate = \'N\'', (
                        row[_CSV_COLUMNS['name']],
                    ))
                
            elif _TASK_NAMES[5] in row[_CSV_COLUMNS['task_name']]:
                # Return
                if isSet(row[_CSV_COLUMNS['return_did_profile']]) and isSet(row[_CSV_COLUMNS['return_did_resume']]):
                    cur.execute('UPDATE results SET return = \'Y\', updateCnt = updateCnt + 1 WHERE name = ? and return = \'N\'', (
                        row[_CSV_COLUMNS['name']],
                    ))
                
            con.commit()

    con.close()

def isSet(val):
    return val in ['Yes', '1', 'TRUE']

def exitFunc():
    print "\nPress enter to close"
    raw_input()
    exit()

main()
