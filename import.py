import re
import sqlite3

first_sql = '''
insert into exam_question (subelement, section, number, reference, text, revoked, image) values (?, ?, ?, ?, ?, ?, ?)
'''
second_sql = '''
insert into exam_answer (text, question_id) values (?, ?)
'''
third_sql = '''
update exam_question set correct_id = ? where id = ?
'''

question_prefix_re = re.compile(r'^(?P<subelement>G\d)(?P<section>[A-Z])(?P<number>\d\d) \((?P<correct>[A-D])\)(?P<reference> .+)?$')
answer_re = re.compile(r'^(?P<answer_letter>[A-D]?)\. (?P<answer>.+)$')
end_question_re = re.compile(r'^~~$')

current_question = None
current_answer = None
infile = open('2007GeneralPrepped.txt', 'r')
question = ''
subelement = None
section = None
number = None
correct = None
reference = ''
answers = {}
for line in infile:
   line = line.strip()
   qmatch = question_prefix_re.search(line)
   ansmatch = answer_re.search(line)
   endmatch = end_question_re.search(line)
   if qmatch:
      subelement = qmatch.group('subelement')
      section = qmatch.group('section')
      number = qmatch.group('number')
      correct = qmatch.group('correct')
      reference = qmatch.group('reference').strip() if qmatch.group('reference') is not None else ''
      current_question = (subelement, section, number)
   elif ansmatch:
      answers[ansmatch.group('answer_letter')] = ansmatch.group('answer')
      current_answer = ansmatch.group('answer_letter')
   elif endmatch:
      print subelement, section, number, correct, reference, question, str(answers)
      db_conn = sqlite3.connect('hamexam_sqlite.db')
      db_cursor = db_conn.cursor()
      db_cursor.execute(first_sql, (subelement, section, number, reference, question.strip(), False, ''))
      db_cursor.execute('select id from exam_question where subelement = ? and section = ? and number = ?', (subelement, section, number))
      new_question_id = db_cursor.fetchone()[0]
      for letter, answer in answers.iteritems():
         db_cursor.execute(second_sql, (answer, new_question_id))
         if correct == letter:
            db_cursor.execute('select id from exam_answer where text = ? and question_id = ?', (answer, new_question_id))
            db_cursor.execute(third_sql, (db_cursor.fetchone()[0], new_question_id))
      current_question = None
      current_answer = None
      question = ''
      answers = {}
      db_conn.commit()
   else:
      if current_question is not None:
         if current_answer is None:
            question += ' ' + line
         else:
            answers[current_answer] += ' ' + line


