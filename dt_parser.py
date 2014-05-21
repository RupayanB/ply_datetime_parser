#!/usr/bin/python

tokens = (
    'DAY', 
    'MONTH', 
    'KWORD', 
    'WORDS',
    'DIGITS',
    'YEAR', 
    'AMPM',
    'LITERALS',
    'TZ',
    'LPAREN',
    'RPAREN',
    'PLUSMINUS',
    'OTHERS',
    )

# TOKENS DEFINITIONS
# All tokens defined by functions are added in the same order as they appear below:

def t_DAY(t):
    r'((monday)|(tuesday)|(wednesday)|(thursday)|(friday)|(saturday)|(sunday))'
    return t

def t_MONTH(t):
    r"(?i)((january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december))"
    return t

def t_KWORD(t):
    r"(?i)((today)|(tomorrow)|(yesterday)|(day after tomorrow)|(day before yesterday))"
    return t

def t_WORDS(t):
    r"(?i)\b((from)|(to)|(until)|(at)|(in)|(till)|\-)\b"
    return t

def t_AMPM(t):
    r"(?i)(am)|(pm)"
    return t

def t_YEAR(t):
    r"\d{4}"
    return t

def t_DIGITS(t):
    r'((\d{2}|\d{1}))'
    return t

def t_LITERALS(t):
    r'\.|\:|\'|\"'
    return t

def t_TZ(t):
    r"(est)|(pst)|(utc)|(cdt)"
    # r'([a-zA-Z]{4})|([a-zA-Z]{3})'
    return t

def t_OTHERS(t):
    r'\S+'
    return t


t_LPAREN = r'\('
t_RPAREN = r'\)'
t_PLUSMINUS = r'\+|\-'
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

# Parsing rules

def p_text(t):
    '''text : text root
            | text other_words
            | text LITERALS
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
    if type(t[1]) is str:
        t[0] = t[1]
    else:
        t[0] = "<tag start=\'" + str(t[1]) + "\'/>"

def p_other_words(t):
    '''other_words : OTHERS
                   | DIGITS
                   | YEAR'''
    if len(t) == 2:
        t[0] = t[1]

def p_expression(t):
    '''expression : date_time
                  | time_exp 
                  | date
                  | date_time expression
                  | time_exp expression'''
    if len(t) == 2:
        t[0] = t[1]
    else:
        if type(t[2]) is datetime.time:
            end_dt = datetime.datetime.combine(today,t[2])
        else:
            # it is already a datetime.datetime object
            end_dt = t[2]
        t[0] = "<tag start=\'" + str(t[1]) + "\' end=\'" + str(end_dt) + "\' />"

def p_datetime(t):
    '''date_time : date time_exp'''
    t[0] = datetime.datetime.combine(t[1], t[2])

def p_date(t):
    '''date : key_word
            | date_exp
            | date date_exp'''
    if len(t) == 2:
        t[0] = t[1]
    else:
        # special case: today 15 May 2014, ignores 'today'
        t[0] = t[2]

def p_date_exp(t):
    '''date_exp : date_order1
                | date_order2 '''
    t[0] = t[1]

def p_date_order1(t):
    '''date_order1 : MONTH DIGITS
                   | MONTH DIGITS YEAR'''
    mm = monthsMap[t[1].lower()]
    dd = int(t[2])
    if len(t) == 4:
        yy = int(t[3])
    else:
        yy = today.year
    date = datetime.date(yy,mm,dd)

    t[0] = date

def p_date_order2(t):
    'date_order2 : DIGITS MONTH YEAR'
    dd = int(t[1])
    mm = monthsMap[t[2].lower()]
    yy = int(t[3])
    date = datetime.date(yy,mm,dd)
    t[0] = date


def p_keyword(t):
    'key_word : KWORD'
    delta = datetime.timedelta(abs(kwDiffs[t[1].lower()]))
    if kwDiffs[t[1].lower()] < 0:
        day = today - delta
    else:
        day = today + delta
    t[0] = day
    
def p_time(t):
    '''time_exp : DIGITS LITERALS DIGITS 
                | time_exp AMPM
                | time_exp time_zone'''
    if len(t) == 2:
        t[0] = datetime.time(int(t[1]),0)
    elif len(t) == 4:
        hrs = int(t[1])
        mins = int(t[3])
        t[0] = datetime.time(hrs, mins)
    else:
        if t[2] == 'pm' and t[1].hour != 12:
            dt = datetime.datetime.combine(today,t[1]) + timedelta(hours=12)
            t[0] = dt.time()
        elif t[2] == 'am' and t[1].hour == 12:
            dt = datetime.datetime.combine(today,t[1]) - timedelta(hours=12)
            t[0] = dt.time()
        else:
            t[0] = t[1]

def p_timezone(t):
    '''time_zone : TZ
                 | LPAREN time_zone RPAREN
                 | time_zone PLUSMINUS DIGITS'''
    t[0] = ''  

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


