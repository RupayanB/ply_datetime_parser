#!/usr/bin/python

import re
from ply.lex import TOKEN

"""
REGULAR EXPRESSIONS
"""
#Simple reg exps to be used to build more complex tokens

#hours minutes
hhmm = r'(\d+[\.\:]{1}\d+\s*([apmAPM]{2})?)'
#timezone
tz = r"(?i)((\()?((est)|(edt)|(pst)|(utc)|(cdt)|(cest))(\))?\s*([\+\-]\d+)?)?"
#special connecting words. eg: from 5:00pm till 8:00pm
conn = r'(?i)((from)|(to)|(until)|(at)|(in)|(till)|\-)?'
#digits representing days (can be followed by 2 letter sequences and 'of', eg. 5th of May)
dd = r'(?i)(\d{2}|\d{1})((th)|(st)|(nd)|(rd))?(\sof)?'
#digits representing months
mm = r'(?i)((january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december))'
#special keywords that can represent days
kw = r"(?i)((today)|(tomorrow)|(yesterday)|(day\s{1}after\s{1}tomorrow)|(day\s{1}before\s{1}yesterday))"
#digits
dig = r"[0-9]+"
#buffer chars eg. 5th of May, 2014 
buff = r'[\s\,]*'

# regular expressions for tokens
time = hhmm + buff + tz + buff + conn
ddmm = dd + buff + mm + buff + conn
mmdd = mm + buff + dd + buff + conn
kword = kw + buff + conn
digits = dig + buff + conn

tokens = (
    'DAY',
    'DDMM',
    'MMDD', 
    'KWORD',
    'TIME',
    'LITERALS',
    'WORDS',
    'DIGITS',
    )

"""
TOKENS DEFINITIONS
"""

def t_DAY(t):
    r'(?i)((monday)|(tuesday)|(wednesday)|(thursday)|(friday)|(saturday)|(sunday))'
    return t

# use @TOKEN if the token is to be defined using the "regular expressions for tokens" above

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
    r'\.|\:|\'|\"|\,|\(|\)|\!|\?|\\|\/|\#'
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

"""
PARSER
"""

#helper variables and data structures for rules evaluation:

today = datetime.date.today()
#maps for evaluating datetime expressions
kwDiffs = {'today':0,'yesterday':-1,'tomorrow':1,'day before yesterday':-2,'day after tomorrow':2}
monthsMap = {'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,'july':7,'august':8,'september':9,\
        'october':10,'november':11,'december':12}
#regular exps 
months = r'(?i)((january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december))'
keywords = r"(?i)((today)|(tomorrow)|(yesterday)|(day after tomorrow)|(day before yesterday))"
#variable used to rebuild original expression (for inserting between tags)
original = ''

# PARSER RULES
#note: uses length of rules (number of tokens, including LHS) to determine matching rule

#entire text
def p_text(t):
    '''text : text dt_root
            | text words
            | empty'''
    if len(t) == 2:
        t[0] = ''
    else:
        t[0] = t[1] + ' ' + t[2] 


def p_empty(t):
    'empty :'
    pass

#root of date time expressions
def p_root(t):
    'dt_root : expression'
    global original
    if type(t[1]) is str:
        t[0] = t[1]
    else:
        t[0] = "<tag start=\'" + str(t[1]) + "\'> " + original + " </tag>" 
        #reset variable for original expression
        original = ''

#everything else
def p_other_words(t):
    '''words : WORDS
             | DIGITS
             | LITERALS
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
                #combine t[1]'s date with t[2]'s time to produce a datetime object
                #this is used for expressions in which the end date is assumed to be same as start date
                startDate = t[1].date()
                end_dt = datetime.datetime.combine(startDate,t[2])
            else:
                end_dt = t[2]
        else:
            # it is already a datetime.datetime object
            end_dt = t[2]
        t[0] = "<tag start=\'" + str(t[1]) + "\' end=\'" + str(end_dt) + "\'> " + original + " </tag>" 
        original = ''

    else:
        #same as above, except for the redundant DAY 
        if type(t[3]) is datetime.time:
            startDate = t[1].date()
            end_dt = datetime.datetime.combine(startDate,t[3])
        else:
            # it is already a datetime.datetime object
            end_dt = t[3]
        t[0] = "<tag start=\'" + str(t[1]) + "\' end=\'" + str(end_dt) + "\'> " + original + " </tag>" 
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
        #build original expression
        original += t[2] + ' '
        mm = t[1].month
        dd = t[1].day
        # Here DIGITS represent the year
        year = re.search(r'[0-9]+',t[2]).group(0)
        yy = int(year)
        t[0] = datetime.date(yy,mm,dd)

# example: May 1st
def p_monthday(t):
    'month_day : MMDD'
    global months, original
    #build original expression
    original += t[1] + ' '
    #extract digits representing day, eg: if expr is 5th of May, then extract '5' and store in day
    day = re.search(r'(\d{2}|\d{1})',t[1]).group(0)
    dd = int(day)
    month = re.search(months,t[1]).group(0)
    #convert month to digits
    mm = monthsMap[month.lower()]
    yy = today.year
    t[0] = datetime.date(yy,mm,dd)

#example: 1st May
def p_daymonth(t):
    'day_month : DDMM'
    global months, original
    #build original expression
    original += t[1] + ' '
    #extract digits representing day, eg: if expr is 5th of May, then extract '5' and store in day
    day = re.search(r'(\d{2}|\d{1})',t[1]).group(0)
    dd = int(day)
    month = re.search(months,t[1]).group(0)
    #convert month to digits
    mm = monthsMap[month.lower()]
    yy = today.year
    t[0] = datetime.date(yy,mm,dd)

def p_keyword(t):
    'key_word : KWORD'
    global keywords, original
    #build original expression
    original += t[1] + ' ' 
    kw = re.search(keywords,t[1]).group(0).lower()
    delta = datetime.timedelta(abs(kwDiffs[kw]))
    # negative values indicate before today, and positive indicates after today
    if kwDiffs[kw] < 0:
        day = today - delta
    else:
        day = today + delta
    t[0] = day
    
def p_time(t):
    '''time_exp : TIME'''
    global original
    #build original expression
    original += t[1] + ' '

    #extract hours minutes from time expression
    hhmm = r'\d+[:\.]+\d+'
    m =  re.search(hhmm, t[1]).group(0)
    tlist = [int(x) for x in re.split(':|\.', m)]

    #create time object
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
        
    #TODO  time zone 

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
    try:
        fd = open(fname)
    except:
        print "Invalid filename."
        exit(1)
    for line in fd:
        print str(yacc.parse(line.strip()))

    fd.close()

def command_line():
    while 1:
        try:
            print
            s = raw_input('expr > ') 
        except EOFError:
            break
        print str(yacc.parse(s))


if __name__ == '__main__':
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],'ct')
    except Exception as inst:
        print 'ERROR!\n' + str(inst)
        exit(1)
    if len(opts) == 0:
        command_line()
    else:
        for opt, arg in opts:
            if opt == '-c':
                command_line()
            if opt == '-t':
                test_mode()


