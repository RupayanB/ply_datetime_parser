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

Usage
-----

Default usage:
$ ./dt2.py

expr > The event is on May 05, at 15:00.
 The event is on <tag start='2014-05-05 15:00:00'> May 05, at 15:00  </tag> .

Alternatively, use option -t (test mode) for evaluating a list of expressions from a file:

$ ./dt2.py -t
file: test1.txt
 <tag start='2014-06-02 17:00:00'> Today  5:00pm  </tag>
 Tuesday <tag start='2014-02-25 19:00:00'> February 25  2014  7:00 PM  </tag>
 Sunday <tag start='2014-03-09 17:30:00' end='2014-03-09 19:00:00'> 9 March  2014 from 17:30 to 19:00 (CDT)  </tag>
 <tag start='2014-06-02 15:00:00' end='2014-06-02 17:00:00'> Today  3:00pm until 5:00pm  </tag>
 <tag start='2014-06-02'> Today  </tag>
 
 
