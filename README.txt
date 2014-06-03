ply_datetime_parser
===================

A tool to parse, tag and evaluate date and time expressions, including ranges, in unstructured text.

Examples:
<tag start='2014-06-02 17:00:00'> Today  5:00pm  </tag>
<tag start='2014-03-11'> March 11  2014  </tag>
<tag start='2014-06-04'> day after tomorrow  </tag>
<tag start='2014-06-06'> 6th of June,  2014  </tag>
<tag start='2014-06-02 15:00:00' end='2014-06-02 17:00:00'> Today  3:00pm until 5:00pm  </tag>
<tag start='2014-03-07 12:00:00' end='2014-03-11 15:00:00'> March 7  2014 at 12:00 PM - March 11  2014 at 3:00 PM  </tag>

Requirements:
Language: Python 2.7 
Packages/Libraries: ply, datetime, re, getopt

Usage
-----

Default usage:
$ ./dt2.py

expr > The event is on May 05, at 15:00.
 The event is on <tag start='2014-05-05 15:00:00'> May 05, at 15:00  </tag> .

Alternatively, use option -t (test mode) for evaluating a list of expressions from a file (each expression on a new line):

$ ./dt2.py -t
file: test1.txt
 <tag start='2014-06-02 17:00:00'> Today  5:00pm  </tag>
 Tuesday <tag start='2014-02-25 19:00:00'> February 25  2014  7:00 PM  </tag>
 Sunday <tag start='2014-03-09 17:30:00' end='2014-03-09 19:00:00'> 9 March  2014 from 17:30 to 19:00 (CDT)  </tag>
 <tag start='2014-06-02 15:00:00' end='2014-06-02 17:00:00'> Today  3:00pm until 5:00pm  </tag>
 <tag start='2014-06-02'> Today  </tag>
 
 Design
------
The tool consists of 3 main parts:
1. Regular expressions
	Defines the simple building blocks for defining tokens. The idea behind building tokens by putting together multiple regular expressions is to prevent the lexer from confusing characters that form date-time expressions from those that are not part of such expressions. This also leads to simpler rules for the grammar. For example, consider "5th of May, 2014". By including connecting words such as 'of' and characters like ',' in the token definition for DDMM (day-month), the responsibility of recognizing that these words and characters are part of the same expression and not two different expressions, is off-loaded from the parser to the lexer. The parser then merely has to use the rule for day_month DIGITS, where DIGITS represents the year. 
	This approach attempts to minimize shift-reduce conflicts. 

2. Token Definitions
	Tokens are defined either using the regular expressions described above, or independently (ie, within the token method). Use '@TOKEN' if the regular expressions above are used. 
	NOTE: The lexer internally further generates regular expressions for the token definitions in the same order as they are listed under token definitions. Therefore, larger regular expressions should be listed above shorter ones to prevent unexpected errors.

3. Grammar
	Defines a set of rules for recognizing date-time expressions embedded in text, as well as the code for evaluating those expressions and returning python datetime objects. The rule 'p_text' is the actual root of the grammar. 'p_root' is the root for the grammar that describes date-time expressions. Since python's ply package does not provide a means for matching rules with actions, the length of the rules (or number of tokens including lhs) is used to determine which block of code should be executed. 


Extending the tool
------------------
The tool can be extended in any of the following ways:

1. Modifying existing tokens
This is the simplest way to extend the tool. For example, to support shortened versions of month and weekday nouns ('jan' or 'mon'), simply add the shortened version to the existing regular expressions using the '|' operator (see 'mm' and 't_DAY'). Similarly, new time zones can be added by modifying the 'tz' regular expression.

2. Adding new rules
Create new parser rules to recognize new date-time expressions. For example, currently the rules support expressions that start with date. A new rule, called 'p_timedate' (similar to 'p_datetime') could be defined that describes expressions that start with the time. This rule would then have to be added to the 'p_expression' rules. The corresponsing code would also have to handle these new expressions. Here, since the length of the rules is unlikely to change, python's type operator can be used to determine the type of the tokens.

3. Create new tokens and rules
To add support for new tokens, follow either of the following two approaches:
	i. If the token is not required for evaluating a date-time expression, then define the token independently of the regexp building blocks defined at the top. Example: The t_DAY was defined for weekday strings like 'Monday'. Days are often redundant and are not used to evaluating the date. However, including them in the p_expression rule, allows the parser to recognize complex expressions ignoring the DAY embedded inside it.
	ii. If the token is required for evaluating a date-time expression, then first 'build' the token using the regular expressions described at the top. For example, to add support for a word like 'noon' (ie. 12:00 pm), first create a regex variable for noon. Next, create another regex variable by appending to the first variable, the variables buff and finally conn. This ensures that connecting words like 'to' and 'from' are glued to the keyword noon when it is consumed by the lexer. Finally, use this regex variable to define a new token using '@TOKEN' and adding it to the list of tokens.
Once the token has been defined (and added to the token list), it is ready for inclusion in a new rule. 
 
 
