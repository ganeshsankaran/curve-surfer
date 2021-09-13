from collections import OrderedDict
from django.db import connection
import re
import statistics

# Get a list of course numbers
def get_cnums():
    return listify(sort_by_cnum(
        get_record_set(GET_CNUMS_QUERY)
    ))

# Get a list of instructors
def get_instrs():
    return listify(get_record_set(GET_INSTRS_QUERY))

# Get a list of quarters/years
def get_qtrs():
    return listify(get_record_set(GET_QTRS_QUERY))

# Get letter grade distribution
# letter -> num
def get_letter_grade_dist(d):
    return dictify(get_record_set(
        GET_LETTER_GRADE_DIST_QUERY.format(get_conjunction_expr(d))
    ))

# Get statistics for GPA
def get_letter_grade_dist_stats(d):
    data = get_values_from_freq_dist(get_record_set(
        GET_GPA_DIST_QUERY.format(get_conjunction_expr(d))
    ))
    
    return get_descriptive_stats(data)

# Get average gpa and # students per course number
def get_avg_gpa_per_cnum(d):
    if d['cnum']:   
        return None, None

    record_set = get_record_set(
        GET_AVG_GPA_PER_CNUM_QUERY.format(get_conjunction_expr(d))
    )

    return dictify(record_set), sort_by_cnum(record_set)

# Get average gpa and # students per instructor
def get_avg_gpa_per_instr(d):
    if d['instr']:
        return None, None

    record_set = get_record_set(
        GET_AVG_GPA_PER_INSTR_QUERY.format(get_conjunction_expr(d))
    )

    return dictify(record_set), sort_by_instr(record_set)

# Get average gpa per quarter
def get_avg_gpa_per_qtr(d):
    if d['qtr']:
        return None

    return dictify(get_record_set(
        GET_AVG_GPA_PER_QTR_QUERY.format(get_conjunction_expr(d))
    ))

# Constants

GET_CNUMS_QUERY = '''
select distinct cnum 
from Grades
where dept = 'CMPSC'
order by cnum;
'''

GET_INSTRS_QUERY = '''
select distinct instr 
from Grades
where dept = 'CMPSC'
order by instr;
'''

GET_QTRS_QUERY = '''
select concat(qtr, ' ', yr)
from Grades
where dept = 'CMPSC'
group by qtr, yr
order by 
    yr,
    (case qtr
        when 'Winter' then 0
        when 'Spring' then 1
        when 'Summer' then 2
        when 'Fall' then 3
    end);
'''

GET_LETTER_GRADE_DIST_QUERY = '''
select
    grade,
    sum(freq),
    gpa
from Grades
where
    grade not in ('P', 'NP', 'S', 'U')
    and {}
group by 
    grade, 
    gpa
order by 
    gpa desc, 
    grade desc;
'''

GET_GPA_DIST_QUERY = '''
select
    gpa,
    sum(freq)
from Grades
where
    grade not in ('P', 'NP', 'S', 'U')
    and {}
group by gpa
'''

GET_AVG_GPA_PER_CNUM_QUERY = '''
select 
    cnum,
    sum(gpa * freq) / sum(freq) as avggpa,
    sum(freq)
from Grades
where 
    grade not in ('P', 'NP', 'S', 'U')
    and {}
group by cnum
order by 
    avggpa desc,
    cnum;
'''

GET_AVG_GPA_PER_INSTR_QUERY = '''
select 
    instr,
    sum(gpa * freq) / sum(freq) as avggpa,
    sum(freq)
from Grades
where
    grade not in ('P', 'NP', 'S', 'U')
    and {}
group by instr
order by 
    avggpa desc,
    instr;
'''

GET_AVG_GPA_PER_QTR_QUERY = '''
select 
    concat(qtr, ' ', yr) as qtryr,
    sum(gpa * freq) / sum(freq) as avggpa
from Grades
where 
    grade not in ('P', 'NP', 'S', 'U')
    and {}
group by qtr, yr
order by 
    yr,
    (case qtr
        when 'Winter' then 0
        when 'Spring' then 1
        when 'Summer' then 2
        when 'Fall' then 3
    end);
'''

# Helpers

# Run a query and get results
def get_record_set(query):
    cursor = connection.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# Split a qtr/yr combo into quarter and year
# ex. "Fall 2020" -> "Fall", "2020"
def split_qtr_and_yr(d):
    if not d['qtr'] or ' ' not in d['qtr']:
        return d
    
    qtr, yr = d['qtr'].split(' ')
    d['qtr'] = qtr
    d['yr'] = yr
    
    return d

# Build a SQL AND clause
def get_conjunction_expr(d):
    return ' and '.join(['{} = \'{}\''.format(k, v) for k, v in d.items() if v])

# Get all the data points given a 
# frequency distribution table (as a dict)
def get_values_from_freq_dist(record_set):
    data = []
    
    for record in record_set:
        data += [record[0]] * record[1]
    
    return data

# Compute some stats on data points
def get_descriptive_stats(l):
    if len(l) == 0:
        return None

    return {
        'n': len(l),
        'min': min(l),
        'max': max(l),
        'mean': statistics.mean(l),
        'median': statistics.median(l),
        'mode': statistics.mode(l),
        'stdev': statistics.stdev(l),
        'quantiles': statistics.quantiles(l)
    }

# Split a course into numeric and alpha parts
# ex. "190DD" -> "190", "DD"
def split_cnum_prefix_and_suffix(cnum):
    p, s = re.match('^([0-9]+)([A-Z]*)$', cnum).groups()

    return (p, s)

# Sort a record set by the course number
def sort_by_cnum(record_set, cnum_idx = 0):
    d = {record[cnum_idx]: record for record in record_set}
    l = []

    for cnum in d.keys():
        l.append(split_cnum_prefix_and_suffix(cnum))

    l = sorted(l, key=lambda p: (int(p[0]), p[1]))
    
    return [d[''.join(cnum)] for cnum in l]

# Sort a record set by the instructor name
def sort_by_instr(record_set, instr_idx = 0):
    return sorted(record_set, key=lambda t: t[instr_idx])

# Convert a record set to a dict
def dictify(record_set):
    return OrderedDict((record[0], record[1]) for record in record_set)

# Convert a record set into a list
def listify(record_set):
    return [record[0] for record in record_set]