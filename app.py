import sqlite3 as sql
import csv

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
_TASK_FIELDS = (
    ('Power of One', 'po_min_hours', 'po_total_hours'),
    ('One to Many', 'om_number_attended', 'om_university'),
    ('One Data Point', 'od_completed'),
    ('One Voice', 'ov_completed'),
    ('One Idea', 'oi_submitted_idea', 'oi_meets_net_worth'),
    ('One to Return', 'or_completed')
)

_DB_FILE = 'legacy.db'

def main():
    print "Setting up database"
    initDatabase()
    print "Importing survey into database"
    csv2sql()
    print "Done!"

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
            
            if _TASK_FIELDS[0][0] in row[_CSV_COLUMNS['task_name']]:
                # Power of One
                cur.execute('UPDATE results SET po_min_hours = ?, po_total_hours = ? WHERE name = ?', (
                    '1' if row[_CSV_COLUMNS['po_min_hours']] == 'Yes' else '0',
                    row[_CSV_COLUMNS['po_total_hours']],
                    row[_CSV_COLUMNS['name']]
                ))
                
            elif _TASK_FIELDS[1][0] in row[_CSV_COLUMNS['task_name']]:
                # One to Many
                cur.execute('UPDATE results SET om_number_attended = ?, om_university = ? WHERE name = ?', (
                    row[_CSV_COLUMNS['om_number_attended']],
                    row[_CSV_COLUMNS['om_university']],
                    row[_CSV_COLUMNS['name']]
                ))
                
            elif _TASK_FIELDS[2][0] in row[_CSV_COLUMNS['task_name']]:
                # One Data Point
                cur.execute('UPDATE results SET od_completed = ? WHERE name = ?', (
                    'T' if row[_CSV_COLUMNS['od_completed']] == 'TRUE' else 'F',
                    row[_CSV_COLUMNS['name']]
                ))
                
            elif _TASK_FIELDS[3][0] in row[_CSV_COLUMNS['task_name']]:
                # One Voice
                cur.execute('UPDATE results SET ov_completed = ? WHERE name = ?', (
                    'T' if row[_CSV_COLUMNS['ov_completed']] == 'Yes' else 'F',
                    row[_CSV_COLUMNS['name']]
                ))
                
            elif _TASK_FIELDS[4][0] in row[_CSV_COLUMNS['task_name']]:
                # One Idea
                cur.execute('UPDATE results SET oi_submitted_idea = ?, oi_meets_net_worth = ? WHERE name = ?', (
                    'T' if row[_CSV_COLUMNS['oi_submitted_idea']] == 'TRUE' else 'F',
                    'T' if row[_CSV_COLUMNS['oi_meets_net_worth']] == 'TRUE' else 'F',
                    row[_CSV_COLUMNS['name']]
                ))
                
            elif _TASK_FIELDS[5][0] in row[_CSV_COLUMNS['task_name']]:
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