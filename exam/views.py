from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.db import connection
from hamexam.exam.models import Question, Answer

import random

# Create your views here.
def index(request):
   random.seed()
   exam = []
   cursor = connection.cursor()
   cursor.execute('select distinct subelement from exam_question')
   subelements = cursor.fetchall()
   for subelement in subelements:
      subelement = subelement[0]
      cursor.execute('select distinct section from exam_question where subelement = %s', [subelement,])
      sections = cursor.fetchall()
      for section in sections:
         question = {}
         section = section[0]
         cursor.execute('select distinct number from exam_question where subelement = %s and section = %s and not revoked', [subelement, section])
         numbers = cursor.fetchall()
         tempnumbers = [number[0] for number in numbers]
         number = random.choice(tempnumbers)
         cursor.execute('select q.text, q.correct_id, q.image, q.reference, a.id, a.text from exam_question q join exam_answer a on a.question_id = q.id where subelement = %s and section = %s and number = %s', [subelement, section, number])
         question_and_answers = cursor.fetchall()
         question['text'] = question_and_answers[0][0]
         question['correct_answer_id'] = question_and_answers[0][1]
         question['image'] = question_and_answers[0][2] if len(question_and_answers[0][2]) != 0 else None
         question['reference'] = question_and_answers[0][3] if len(question_and_answers[0][3]) != 0 else None
         random.shuffle(question_and_answers)
         question['answers'] = {}
         for answer in question_and_answers:
            question['answers'][answer[4]] = answer[5]
         question['subelement'] = subelement
         question['section'] = section
         question['number'] = number

         exam.append(question)
         
   return render_to_response('exam/exam.html', {'exam': exam})

def grade_exam(request):
   cursor = connection.cursor()
   exam = []
   correct_answers = {}
   given_answers = {}
   for key in request.POST.keys():
      split_result = key.rsplit('_correct', 1)
      if len(split_result) == 2:
         correct_answers[split_result[0]] = request.POST[split_result[0] + '_correct']
      if len(split_result) == 1:
         given_answers[split_result[0]] = request.POST[split_result[0]]

   num_correct = 0
   num_incorrect = 0
   the_keys = correct_answers.keys()
   the_keys.sort()
   for k in the_keys:
      v = correct_answers[k]
      question = {}
      subelement = k[0:2]
      section = k[2:3]
      number = k[3:5]
      cursor.execute('select q.text, q.correct_id, q.image, q.reference, a.id, a.text from exam_question q join exam_answer a on a.question_id = q.id where subelement = %s and section = %s and number = %s', [subelement, section, number])
      question_and_answers = cursor.fetchall()
      question['text'] = question_and_answers[0][0]
      question['correct_answer_id'] = str(question_and_answers[0][1])
      question['image'] = question_and_answers[0][2] if len(question_and_answers[0][2]) != 0 else None
      question['reference'] = question_and_answers[0][3] if len(question_and_answers[0][3]) != 0 else None
      random.shuffle(question_and_answers)
      question['answers'] = {}
      for answer in question_and_answers:
         question['answers'][str(answer[4])] = answer[5]
      question['subelement'] = subelement
      question['section'] = section
      question['number'] = number
      question['given_answer_id'] = str(given_answers[k]) if k in given_answers else None
      if k in given_answers and v == given_answers[k]:
         num_correct += 1
      else:
         num_incorrect += 1

      exam.append(question)

   return render_to_response('exam/grade.html', {'exam': exam, 'num_correct': num_correct, 'score': 100 * float(num_correct)/float(num_correct + num_incorrect)})

