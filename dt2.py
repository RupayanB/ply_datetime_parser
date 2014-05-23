#!/usr/bin/python

import re
from ply.lex import TOKEN

# REGEX
ddhh = r'(\d+[\.\:]{1}\d+\s*([apmAPM]{2})?)'
tz = r"(?i)((\()?((est)|(edt)|(pst)|(utc)|(cdt)|(cest))(\))?\s*([\+\-]\d+)?)?"
conn = r'(?i)((from)|(to)|(until)|(at)|(in)|(till)|\-)?'
dd = r'(?i)(\d{2}|\d{1})((th)|(st)|(nd)|(rd))?'
mm = r'(?i)((january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december))'
kw = r"(?i)((today)|(tomorrow)|(yesterday)|(day after tomorrow)|(day before yesterday))"
dig = r"[0-9]+"
buff = r'\s*'

time = ddhh + buff + tz + buff + conn
ddmm = dd + buff + mm + buff + conn
mmdd = mm + buff + dd + buff + conn
kword = kw + buff + conn
digits = dig + buff + conn

tokens = (
    'DAY',
    'DDMM',
    'MMDD', 
    'KWORD', 
    'CONN',
    'WORDS',
    'DIGITS',
    'LITERALS',
    'TIME',
    )

# TOKENS DEFINITIONS
# All tokens defined by functions are added in the same order as they appear below:

def t_DAY(t):
    r'(?i)((monday)|(tuesday)|(wednesday)|(thursday)|(friday)|(saturday)|(sunday))'
    return t

@TOKEN(ddmm)
def t_DDMM(t):
    return t

@TOKEN(mmdd)
def t_MMDD(t):
    return t

@TOKEN(kword)
def t_KWORD(t):
    return t

@TOKEN(time)
def t_TIME(t):
    return t

def t_LITERALS(t):
    r'\.|\:|\'|\"|\,|\(|\)|\!|\?'
    return t

def t_WORDS(t):
    r"[a-zA-Z]+"
    return t

@TOKEN(digits)
def t_DIGITS(t):
    return t

# Ignored characters
t_ignore = " \t"
 
# error handling 
def t_error(t):
    try:
        print("Illegal character '%s'" % t.value[0])
    except:
        exit(0)
    t.lexer.skip(1)
    
# Build the lexer
import ply.lex as lex
import datetime
from datetime import timedelta
lex.lex()

today = datetime.date.today()
kwDiffs = {'today':0,'yesterday':-1,'tomorrow':1,'day before yesterday':-2,'day after tomorrow':2}
monthsMap = {'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,'july':7,'august':8,'september':9,\
        'october':10,'november':11,'december':12}

months = r'(?i)((january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december))'
keywords = r"(?i)((today)|(tomorrow)|(yesterday)|(day after tomorrow)|(day before yesterday))"

original = ''

precedence = (
    ('left','WORDS'),
    ('left', 'DIGITS','LITERALS'),
    ('left', 'TIME'),
    ('left','DDMM','MMDD'),
)

# Parsing rules

def p_text(t):
    '''text : text root
            | text words
            | empty'''
    if len(t) == 2:
        t[0] = ''
    else:
        t[0] = t[1] + ' ' + t[2] 


def p_empty(t):
    'empty :'
    pass

def p_root(t):
    'root : expression'
    global original
    if type(t[1]) is str:
        t[0] = t[1]
    else:
        t[0] = "<tag start=\'" + str(t[1]) + "\' >" + original + "</tag>" 
        original = ''

def p_other_words(t):
    '''words : WORDS
             | DIGITS
             | LITERALS
             | CONN
             | DAY'''
    if len(t) == 2:
        t[0] = t[1]

def p_expression(t):
    '''expression : time_exp 
                  | date
                  | date_time
                  | date_time expression
                  | date_time DAY expression
                  | time_exp expression'''
    global original
    if len(t) == 2:
        t[0] = t[1]
    elif len(t) == 3:
        
        if type(t[2]) is datetime.time:
            if type(t[1]) is datetime.datetime:
                startDate = t[1].date()
                end_dt = datetime.datetime.combine(startDate,t[2])
            else:
                end_dt = t[2]
        else:
            # it is already a datetime.datetime object
            end_dt = t[2]
        t[0] = "<tag start=\'" + str(t[1]) + "\' end=\'" + str(end_dt) + "\' >" + original + "</tag>" 
        original = ''

    else:
        if type(t[3]) is datetime.time:
            startDate = t[1].date()
            end_dt = datetime.datetime.combine(startDate,t[3])
        else:
            # it is already a datetime.datetime object
            end_dt = t[3]
        t[0] = "<tag start=\'" + str(t[1]) + "\' end=\'" + str(end_dt) + "\' > " + original + "</tag>" 
        original = ''

def p_datetime(t):
    '''date_time : date time_exp'''
    if len(t) == 3:
        t[0] = datetime.datetime.combine(t[1], t[2])
    else:
        t[0] = datetime.datetime.combine(t[1], t[3])

def p_date(t):
    '''date : key_word
            | date_exp'''
    if len(t) == 2:
        t[0] = t[1]

def p_date_exp(t):
    '''date_exp : month_day
                | day_month
                | month_day DIGITS
                | day_month DIGITS'''
    global original
    if len(t) == 2:
        t[0] = t[1]
    else:
        original += t[2] + ' '
        mm = t[1].month
        dd = t[1].day
        year = re.search(r'[0-9]+',t[2]).group(0)
        yy = int(year)
        t[0] = datetime.date(yy,mm,dd)


def p_monthday(t):
    'month_day : MMDD'
    global months, original
    original += t[1]
    day = re.search(r'(\d{2}|\d{1})',t[1]).group(0)
    dd = int(day)
    month = re.search(months,t[1]).group(0)
    mm = monthsMap[month.lower()]
    yy = today.year
    t[0] = datetime.date(yy,mm,dd)


def p_daymonth(t):
    'day_month : DDMM'
    global months, original
    original += t[1] + ' '
    day = re.search(r'(\d{2}|\d{1})',t[1]).group(0)
    dd = int(day)
    month = re.search(months,t[1]).group(0)
    mm = monthsMap[month.lower()]
    yy = today.year
    t[0] = datetime.date(yy,mm,dd)

def p_keyword(t):
    'key_word : KWORD'
    global keywords, original
    original += t[1] + ' ' 
    kw = re.search(keywords,t[1]).group(0).lower()
    delta = datetime.timedelta(abs(kwDiffs[kw]))
    if kwDiffs[kw] < 0:
        day = today - delta
    else:
        day = today + delta
    t[0] = day
    
def p_time(t):
    '''time_exp : TIME'''
    global original
    original += t[1] + ' '

    hhmm = r'\d+[:\.]+\d+'
    m =  re.search(hhmm, t[1]).group(0)
    tlist = [int(x) for x in re.split(':|\.', m)]

    if len(tlist) == 2:
        time = datetime.time(tlist[0], tlist[1])
    elif len(tlist) == 1:
        time = datetime.time(tlist[0], 0)

    #  adjustment for am/pm
    ampm = r'[apmAPM]{2}'
    if re.search(ampm, t[1]) != None:
        m = re.search(ampm, t[1]).group(0).lower()
        if m == 'pm' and time.hour < 12:
            dt = datetime.datetime.combine(today,time) + timedelta(hours=12)
            time = dt.time()
        elif m == 'am' and time.hour == 12:
            dt = datetime.datetime.combine(today,time) - timedelta(hours=12)
            time = dt.time()
        
    # if re.search(tz, t[1]) != None:
        # m = re.search(ampm, t[1]).group(0)
        #TODO insert time zone logic here

    t[0] = time


def p_error(t):
    try:
        print("Parsing error at '%s'" % t.value)
    except:
        print "Parsing error :("

#Build the parser
import ply.yacc as yacc
import sys, getopt
yacc.yacc()

def test_mode():
    fname = raw_input("file: ")
    fd = open(fname)
    count = 1
    for line in fd:
        print str(yacc.parse(line.strip()))
        count += 1

    fd.close()

def command_line():
    while 1:
        try:
            print
            s = raw_input('expr > ')   # Use raw_input on Python 2
        except EOFError:
            break
        print str(yacc.parse(s))


if __name__ == '__main__':
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],'ct')
    except Exception as inst:
        print 'ERROR!' + str(inst)
        exit(1)
    if len(opts) == 0:
        command_line()
    else:
        for opt, arg in opts:
            if opt == '-c':
                command_line()
            if opt == '-t':
                test_mode()


