#!/usr/bin/python
import re
from ply.lex import TOKEN

# REGULAR EXPRESSIONS

day = r'((monday)|(tuesday)|(wednesday)|(thursday)|(friday)|(saturday)|(sunday))'
month = r"((january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december))"
twords = r"((today)|(tomorrow)|(yesterday)|(day after tomorrow)|(day before yesterday))"
year = r"(\d{4})"
dd = r'((\d{2}|\d{1}))'
time = r'(\d+[\.\:]{1}\d+\s*([apmAPM]{2})?)'
tz = r'(((\([a-zA-Z]{3}\))|([a-zA-Z]{3})|(\([a-zA-Z]{4}\))|([a-zA-Z]{4}))\s*([\+\-]\d+)?)'
buff = r'[\sa-zA-Z\-,\+]+'

date1  = month + buff + dd    + buff + year + buff
date2  = dd    + buff + month + buff + year + buff
date3  = month + buff + dd + buff

timetz = time  + buff + tz + buff


###########################################################
# LEXER
###########################################################

tokens = (
    'DATE1',
    'DATE2',
    'DATE3',
    'KWORD',
    'TIME',
    'TIMETZ',
    'OTHERS',
    )

# TOKENS DEFINITIONS


@TOKEN(timetz)
def t_TIMETZ(t):
    return t

@TOKEN(time)
def t_TIME(t):
    return t

@TOKEN(date1)
def t_DATE1(t):
    return t

@TOKEN(date2)
def t_DATE2(t):
    return t

@TOKEN(date3)
def t_DATE3(t):
    return t


def t_KWORD(t):
    r'(?i)(today)|(tomorrow)|(yesterday)|(day after tomorrow)|(day before yesterday)'
    return t

def t_OTHERS(t):
    r'[\S\.]+'
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


###########################################################
# PARSER
###########################################################

today = datetime.date.today()
kwDiffs = {'today':0,'yesterday':-1,'tomorrow':1,'day before yesterday':-2,'day after tomorrow':2}
monthsMap = {'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,'july':7,'august':8,'september':9,\
        'october':10,'november':11,'december':12}
original = ''


#Parsing rules
def p_text(t):
    '''text : text root
            | text OTHERS
            | empty'''
    if len(t) == 2:
        t[0] = ''
    else:
        t[0] = t[1] + ' ' + t[2] 

def p_empty(t):
    'empty :'
    pass

def p_root(t):
    '''root : expression'''
    global original
    if type(t[1]) is str:
        t[0] = t[1]
    else:
        t[0] = "<tag start=\'" + str(t[1]) + "\'> " + original + " </tag>"
        original = ''
        
def p_expression(t):
    '''expression : date
                  | time_exp
                  | key_word
                  | date_time'''
    if len(t) == 2:
        t[0] = t[1]

def p_datetime(t):
    '''date_time : date time_exp'''
    global original
    if len(t) == 3:
        t[0] = datetime.datetime.combine(t[1], t[2])
    else:
        t[0] = datetime.datetime.combine(t[1], t[3])
        
    
def p_date(t):
    '''date : DATE1
            | DATE2
            | DATE3'''
    global original, month, dd, year
    original += t[1] + ' '
    m = re.search(month, t[1].lower()).group(0)
    mm = monthsMap[m.lower()]
    day = int(re.search(dd, t[1]).group(0))

    if re.search(year, t[1]) != None:
        yy = int(re.search(year, t[1]).group(0))
    else:
        yy = today.year
    date = datetime.date(yy,mm,day)
    t[0] = date

def p_keyword(t):
    'key_word : KWORD'
    global original
    original += t[1] + ' '
    delta = datetime.timedelta(abs(kwDiffs[t[1].lower()]))
    if kwDiffs[t[1].lower()] < 0:
        day = today - delta
    else:
        day = today + delta
    t[0] = day


def p_time(t):
    '''time_exp : TIME
                | TIMETZ '''
    global original, tz
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
        m = re.search(ampm, t[1]).group(0)
        if m == 'pm' and time.hour != 12:
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

###########################################################
# END OF PARSER
###########################################################

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


