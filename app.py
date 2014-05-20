import sqlite3 as sql
import csv
from prettytable import PrettyTable


'''
Configuration
'''
_CSV_FILE = 'survey.csv'
# Readable names for CSV column numbers
_CSV_COLUMNS = {
    'task_name': 1,
    'name': 0,
    'campus': 7,
    'po_min_hours': 2,
    'po_total_hours': 3,
    'om_number_attended': 13,
    'om_university': 8,
    'od_completed': 6,
    'ov_completed': 11,
    'oi_submitted_idea': 14,
    'oi_meets_net_worth': 10,
    'or_completed': 4
}

# Match the task with the column names
_TASK_NAMES = (
    'Power of One',
    'One to Many',
    'One Data Point',
    'One Voice',
    'One Idea',
    'One to Return'
)

_DB_FILE = 'legacy.db'

def main():
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
    sum(case when po_min_hours = 'T' then 1 else 0 end) po_cnt,
    sum(case when om_number_attended is not '' AND om_number_attended > 0 then 1 else 0 end) om_cnt,
    sum(case when od_completed = 'T' then 1 else 0 end) od_cnt,
    sum(case when ov_completed = 'T' then 1 else 0 end) ov_cnt,
    sum(case when oi_submitted_idea = 'T' AND oi_meets_net_worth = 'T' then 1 else 0 end) ov_cnt,
    sum(case when or_completed = 'T' then 1 else 0 end) or_cnt
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
    Interns and number of tasks they've completed
    ============================================================
    '''
    # Query Database
    con = sql.connect(_DB_FILE)
    cur = con.cursor()
    cur.execute("""
    SELECT name, campus,
    (
        (case when po_min_hours == 'T' then 1 else 0 end) +
        (case when om_number_attended is not '' AND om_number_attended > 0 then 1 else 0 end) +
        (case when od_completed = 'T' then 1 else 0 end) +
        (case when ov_completed = 'T' then 1 else 0 end) +
        (case when oi_submitted_idea = 'T' AND oi_meets_net_worth = 'T' then 1 else 0 end) +
        (case when or_completed = 'T' then 1 else 0 end)
    ) as tasks_completed
    FROM results
    """)
    results = cur.fetchall()
    con.close()
    
    # Output Result
    header = ("Name", "Campus", "# Completed")
    x = PrettyTable(header)
    x.sortby = "Name"
    x.padding_width = 1
    x.align = "l"
    
    outfile = open('output.csv', 'wb')
    writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(header)
    
    for row in results:
        if row[2] == len(_TASK_NAMES):
            x.add_row(row)
        writer.writerow(row)
    
    print ""
    print "Most active interns (interns who have completed all tasks)"
    print "Full list of all interns and number of tasks completed is in output.csv"
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
    cur.execute("SELECT	count(*) as numResponses, sum(po_total_hours) as total FROM results WHERE po_min_hours = 'T';")
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
    cur.execute("SELECT count(*) as numResponses, sum(om_number_attended) as total FROM results WHERE om_number_attended is not '' AND om_number_attended > 0;")
    results = cur.fetchone()
    con.close()
    
    # Output Result
    print "{0} interns had lunch with {1} people form their universities".format(*results)
    
    
    

def initDatabase():
    '''
    Setup the SQLite database. Clears existing database if it already exists
    '''
    con = sql.connect(_DB_FILE)
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS results;")
    cur.execute("""CREATE TABLE `results` (
                    `name` TEXT NOT NULL UNIQUE,
                    `campus` TEXT,
                    `po_min_hours` TEXT,
                    `po_total_hours` INT,
                    `om_number_attended` INT,
                    `om_university` TEXT,
                    `od_completed` TEXT,
                    `ov_completed` TEXT,
                    `oi_submitted_idea` TEXT,
                    `oi_meets_net_worth` TEXT,
                    `or_completed` TEXT
                );""")
    con.commit()
    con.close()

def csv2sql():
    '''
    Imports _CSV_FILE data into _DB_FILE with column relationship represented in _CSV_COLUMNS
    '''
    try:
        infile = open('survey.csv', 'rb')
    except IOError:
        print "survey.csv not found."
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
        cur.execute("INSERT OR IGNORE INTO results VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            row[_CSV_COLUMNS['name']],
            row[_CSV_COLUMNS['campus']],
            'T' if row[_CSV_COLUMNS['po_min_hours']] == 'Yes' else 'F',
            row[_CSV_COLUMNS['po_total_hours']],
            row[_CSV_COLUMNS['om_number_attended']],
            row[_CSV_COLUMNS['om_university']],
            'T' if row[_CSV_COLUMNS['od_completed']] == 'TRUE' else 'F',
            'T' if row[_CSV_COLUMNS['ov_completed']] == 'Yes' else 'F',
            'T' if row[_CSV_COLUMNS['oi_submitted_idea']] == 'TRUE' else 'F',
            'T' if row[_CSV_COLUMNS['oi_meets_net_worth']] == 'TRUE' else 'F',
            'T' if row[_CSV_COLUMNS['or_completed']] == 'Yes' else 'F'
        ))
        rowsAffected = cur.rowcount
        con.commit()
        
        if rowsAffected == 0:
            # Insert failed because record already exists, update it
            
            if _TASK_NAMES[0] in row[_CSV_COLUMNS['task_name']]:
                # Power of One
                cur.execute('UPDATE results SET po_min_hours = ?, po_total_hours = ? WHERE name = ?', (
                    '1' if row[_CSV_COLUMNS['po_min_hours']] == 'Yes' else '0',
                    row[_CSV_COLUMNS['po_total_hours']],
                    row[_CSV_COLUMNS['name']]
                ))
                
            elif _TASK_NAMES[1] in row[_CSV_COLUMNS['task_name']]:
                # One to Many
                cur.execute('UPDATE results SET om_number_attended = ?, om_university = ? WHERE name = ?', (
                    row[_CSV_COLUMNS['om_number_attended']],
                    row[_CSV_COLUMNS['om_university']],
                    row[_CSV_COLUMNS['name']]
                ))
                
            elif _TASK_NAMES[2] in row[_CSV_COLUMNS['task_name']]:
                # One Data Point
                cur.execute('UPDATE results SET od_completed = ? WHERE name = ?', (
                    'T' if row[_CSV_COLUMNS['od_completed']] == 'TRUE' else 'F',
                    row[_CSV_COLUMNS['name']]
                ))
                
            elif _TASK_NAMES[3] in row[_CSV_COLUMNS['task_name']]:
                # One Voice
                cur.execute('UPDATE results SET ov_completed = ? WHERE name = ?', (
                    'T' if row[_CSV_COLUMNS['ov_completed']] == 'Yes' else 'F',
                    row[_CSV_COLUMNS['name']]
                ))
                
            elif _TASK_NAMES[4] in row[_CSV_COLUMNS['task_name']]:
                # One Idea
                cur.execute('UPDATE results SET oi_submitted_idea = ?, oi_meets_net_worth = ? WHERE name = ?', (
                    'T' if row[_CSV_COLUMNS['oi_submitted_idea']] == 'TRUE' else 'F',
                    'T' if row[_CSV_COLUMNS['oi_meets_net_worth']] == 'TRUE' else 'F',
                    row[_CSV_COLUMNS['name']]
                ))
                
            elif _TASK_NAMES[5] in row[_CSV_COLUMNS['task_name']]:
                # One to Return
                cur.execute('UPDATE results SET or_completed = ? WHERE name = ?', (
                    'T' if row[_CSV_COLUMNS['or_completed']] == 'Yes' else 'F',
                    row[_CSV_COLUMNS['name']]
                ))
                
            con.commit()

    con.close()
        

def exitFunc():
    print "\nPress enter to close"
    raw_input()

main()