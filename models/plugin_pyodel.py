# -*- coding: utf-8 -*-

""" some administrative tasks required:
A group of managers
A group of evaluators

This can be accomplished with an initial setup action

Managers will create courses and related stuff, assign them evaluators.
They will control evaluators rights.
Lastly, they will manage student subscriptions to courses
(attendance admissions)

Evaluators can assign and edit an attendant's evaluation.
"""

"""
Add this code to a plugin setup action

# By now, just update or insert the groups as needed
db.auth_group.update_or_insert(role="manager",
description="Absolute CRUD rights")
db.auth_group.update_or_insert(role="evaluator",
description="Can evaluate exams")
db.auth_group.update_or_insert(role="editor",
description="Can edit documents")
"""

"""
# Quiz syntax:
# Quiz instructions are interpreted by line (line-breaks terminate them).
# Note that answers will appear in the given order unless sh: (for shuffle)
# is added to each question group:

q: The actual question goes here. Ok?
c: C stands for correct answer (I guess)
i: I'm afraid this is an incorrect answer
i: This too is wrong
i: Another one
s: 1.232 # score for this question
m: # for allowing multiple answers
sh: # add this so the answers are mixed

q: Here's another question. ¿What about it?
c: ...
i: ...
"""

import random
import datetime


##################################################################
################## Plugin style configuration ####################
##################################################################

if not request.extension == "load":
    response.files.append(URL(c="static", f="plugin_pyodel/style.css"))


##################################################################
################## Plugin startup configuration ##################
##################################################################

# Check if wiki tables are defined
if not "wiki_page" in db.tables():
    auth.wiki(resolve=False)

# Checkout configuration function
if not "PLUGIN_PYODEL_ATTENDANCE_CHECKOUT" in globals():
    PLUGIN_PYODEL_ATTENDANCE_CHECKOUT = None

##################################################################
################## Plugin static values sets #####################
##################################################################

PLUGIN_PYODEL_MARKMIN_COMMENT=T("Use MARKMIN or plain text")
PLUGIN_PYODEL_UPPERCASE_ALPHABET = ["A", "B", "C", "D", "E",
                                    "F", "G", "H", "I", "J",
                                    "K", "L", "M", "N", "O",
                                    "P", "Q", "R", "S", "T",
                                    "U", "V", "W", "X", "Y",
                                    "Z"]


##################################################################
################## Plugin basic functions ########################
##################################################################

def plugin_pyodel_update_payment(attendance=None,
                                 student=auth.user_id,
                                 course=None,
                                 code=None,
                                 amount=0.00):
    try:
        if course is None:
            course = db(db.plugin_pyodel_course.code==code\
                        ).select().first()
        else:
            course = db.plugin_pyodel_course[course]
        if attendance is not None:
            attendee = db.plugin_pyodel_attendance[attendance]
        else:
            attendee = db((db.plugin_pyodel_attendance.student==\
                           student) & \
                          (db.plugin_pyodel_attendance.course==\
                           course.id)).select().first()
        try:
            new_amount = attendee.paid + amount
        except TypeError:
            # No previous payment
            new_amount = amount
        attendee.update_record(paid=new_amount)
        if new_amount >= course.cost:
            if not attendee.allowed:
                attendee.update_record(allowed=True)
                plugin_pyodel_attendance_setup(attendee.id)
        return (True, T("Payment updated"))
    except (AttributeError, KeyError), e:
        return (False, str(e))

def plugin_pyodel_get_payment(attendance=None,
                              student=auth.user_id,
                              course=None,
                              code=None):
    if attendance is not None:
        attendee = db.plugin_pyodel_attendance[attendance]
    else:
        if code is not None:
            course = db(db.plugin_pyodel_course.code == \
                        code).select().first()
        else:
            course = db.plugin_pyodel_course[course]
        attendee = db((db.plugin_pyodel_attendance.student==student) & \
                      (db.plugin_pyodel_attendance.course==course.id)\
                       ).select().first()
    return attendee.paid

def plugin_pyodel_student_format(r):
    return "%s %s (%s)" % \
            (db.auth_user[r.student].first_name,
            db.auth_user[r.student].last_name, r.student)

def plugin_pyodel_set_quiz(data, deadline=True):
    """ Update a sandglass from session from quiz data."""

    sandglass = db.plugin_pyodel_sandglass[data["sandglass"]]
    total = 0.0
    answers = set()
    quiz_score = sandglass.quiz.score
    questions = len(data["questions"])
    if quiz_score is None:
      quiz_score = 0.0
    score_per_question = quiz_score/questions

    if deadline:
        if sandglass.ends < request.now:
            raise HTTP(500, T("Quiz timed out"))

    for q, question in data["questions"].iteritems():
        complete = 1
        checked = 0
        score = 0
        if question["multiple"]:
            # count total correct items
            complete = len([x for x in question["answers"] \
                            if question["answers"][x]["correct"]])
        if question["score"]:
            score = score/complete
        else:
            score = score_per_question/complete
        for a, answer in question["answers"].iteritems():
            if a in question["marked"]:
                answers.add("%s:%s" % (q, a))
                if (question["multiple"] in (None, False)) and \
                (checked > 1):
                    break
                if answer["correct"]:
                    total += score
                checked += 1
    sandglass.update_record(score=total,
                            answers=list(answers))


def plugin_pyodel_get_quiz(sandglass_id):
    """ Returns a dict with quiz data.

    Structure:
    data -> questions <int question> -> question
                                     -> answers -> <int answer> -> answer
                                     -> score                   -> correct
                                     -> marked <answer set>     -> score
                                     -> shuffle
                                     -> multiple
                                     -> order <list answers>
         -> current <int question>
         -> order <list questions>
         -> sandglass <int id>
    """
    
    sandglass = db.plugin_pyodel_sandglass[int(sandglass_id)]
    quiz = sandglass.quiz
    body = quiz.body
    data = dict(questions=dict(),
                current=None,
                order=[],
                sandglass=sandglass.id)
    answers = dict()

    if sandglass.answers is not None:
        for answer in sandglass.answers:
            values = answer.split(":")
            q, a = int(values[0]), int(values[1])
            if not q in answers:
                answers[q] = set()
            answers[q].add(a)

    question = 0
    answer = 0

    for i, row in enumerate(body.splitlines()):
        string = row.strip()
        text = string[2:].strip()
        if string.startswith("q:"):
            question += 1
            data["order"].append(question)
            answer = 0
            data["questions"][question] = dict(shuffle=False,
                                               question=text,
                                               score=None,
                                               answers=dict(),
                                               marked=set(),
                                               multiple=False,
                                               exact=False,
                                               order=[])
            shuffle = False
        elif string.startswith("sh:"):
            data["questions"][question]["shuffle"] = True
        elif string.startswith("c:") or string.startswith("i:"):
            answer += 1
            data["questions"][question]["order"].append(answer)
            correct = True
            if string.startswith("i:"):
                correct = False
            data["questions"][question]["answers"][answer] = \
            dict(answer=text, correct=correct)
            if question in answers:
                if answer in answers[question]:
                    data["questions"][question]["marked"].add(answer)
        elif string.startswith("sh:"):
            data["questions"][question]["shuffle"] = True
        elif string.startswith("s:"):
            data["questions"][question]["score"] = \
            float(text)
        elif string.startswith("m:"):
            data["questions"][question]["multiple"] = True

    if quiz.shuffle == True:
        random.shuffle(data["order"])

    for question, value in data["questions"].iteritems():
        if value["shuffle"] == True:
            random.shuffle(value["order"])

    return data


def plugin_pyodel_show_markmin(value, row):
    if request.function == "select" and request.args(1) is None:
        # grids
        if value is not None:
            return value[:20]
        else:
            return value
    else:
        # forms
        return MARKMIN(value)

def plugin_pyodel_show_documents(value, row):
    if value is not None:
        return OL(*[LI(A(item.title,
                         _href=URL(r=request,
                                   c="plugin_pyodel",
                                   f="wiki",
                                   args=[item.slug,
                                   ]))) for item in value])
    else:
        return T("Empty")


# This code was extracted from the following site:
# http://codereview.stackexchange.com/questions/5091/
# python-function-to-convert-roman-numerals-to-integers
# -and-vice-versa
# Author: Anthony Curtis Adler

def plugin_pyodel_int_to_roman (integer):
    returnstring=''
    table=[['M',1000],['CM',900],['D',500],['CD',400],['C',100],
           ['XC',90],['L',50],['XL',40],['X',10],['IX',9],
           ['V',5],['IV',4],['I',1]]

    for pair in table:
        while integer-pair[1]>=0:
            integer-=pair[1]
            returnstring+=pair[0]
    return returnstring

def plugin_pyodel_rom_to_int(string):
    table=[['M',1000],['CM',900],['D',500],['CD',400],['C',100],
           ['XC',90],['L',50],['XL',40],['X',10],['IX',9],
           ['V',5],['IV',4],['I',1]]
    returnint=0
    for pair in table:
        continueyes=True
        while continueyes:
            if len(string)>=len(pair[0]):
                if string[0:len(pair[0])]==pair[0]:
                    returnint+=pair[1]
                    string=string[len(pair[0]):]
                else: continueyes=False
            else: continueyes=False
    return returnint


def plugin_pyodel_attendance_setup(attendance):
    attendance = db.plugin_pyodel_attendance[attendance]
    course = attendance.course
    student = attendance.student

    # Add default evaluations
    template_evaluations = db((db.plugin_pyodel_evaluation.course == \
                               course.id) & \
                              (db.plugin_pyodel_evaluation.template == \
                               True)).select()
    for te in template_evaluations:
        ted = te.as_dict()
        ted["template"] = False
        ted["students"] = [attendance.id,]
        ted["id"] = None
        print "Inserting evaluation", ted
        evaluation_id = db.plugin_pyodel_evaluation.insert(**ted)
        # Create sandglasses, hourglasses and works
        for quiz in te.quizzes:
            print "Inserting sandglass", [quiz, quiz.starts, quiz.ends, te.id]
            db.plugin_pyodel_sandglass.insert(quiz=quiz,
                                              starts=quiz.starts,
                                              ends=quiz.ends,
                                              evaluation=te.id)
        for task in te.tasks:
            print "Inserting work", [task, task.starts, task.ends, te.id]
            db.plugin_pyodel_work.insert(task=task,
                                         starts=task.starts,
                                         ends=task.ends,
                                         evaluation=te.id)
        for test in te.tests:
            print "Inserting hourglass", [test, test.starts, test.ends, te.id]
            db.plugin_pyodel_hourglass.insert(test=test,
                                              starts=test.starts,
                                              ends=ends.test.ends,
                                              evaluation=te.id)

    # Get or create a student's gradebook
    gradebook = db(db.plugin_pyodel_gradebook.student == \
          student).select().first()
    if gradebook is None:
        instances = [instance.id for instance in \
                     db(db.plugin_pyodel_instance).select()]
        gradebook_id = \
        db.plugin_pyodel_gradebook.insert(student=student,
                                          instances=instances)
    else:
        gradebook_id = gradebook.id
        instances = gradebook.instances

    # Get or create course grades
    for instance in instances:
        grade = db((db.plugin_pyodel_grade.instance == instance) & \
                   (db.plugin_pyodel_grade.course == course.id) & \
                   (db.plugin_pyodel_grade.gradebook == \
                    gradebook_id) ).select().first()
        if grade is None:
            grade_id = db.plugin_pyodel_grade.insert(\
                           instance=instance,gradebook=gradebook_id,
                           course=course)



##################################################################
################## Plugin table definitions ######################
##################################################################

db.define_table("plugin_pyodel_stream",
                Field("live", "boolean", default=False),
                Field("name"),
                Field("body", "text",
                      comment=PLUGIN_PYODEL_MARKMIN_COMMENT),
                # embedded html code
                Field("html", "text",
                comment=T("The html code for embedding the video")),
                Field("starts", "datetime"),
                Field("ends", "datetime"),
                Field("tags", "list:string"),
                format="%(name)s"
                )

# the whole course
db.define_table("plugin_pyodel_course",
                Field("subject"),
                Field("active", "boolean", default=False),
                Field("template", "boolean", default=False),
                Field("code"),
                Field("abbreviation"),
                Field("name"),
                Field("description", "text",
                      comment=PLUGIN_PYODEL_MARKMIN_COMMENT), # MARKMIN
                Field("streams", "list:reference plugin_pyodel_stream"),
                Field("body", "text",
                      comment=PLUGIN_PYODEL_MARKMIN_COMMENT), # MARKMIN
                Field("by", "list:reference auth_user"),
                Field("starts", "datetime"),
                Field("documents",
                      "list:reference wiki_page"), # STATIC PAGES
                Field("ends", "datetime"),
                Field("tags", "list:string"),
                Field("cost", "double", default=0.0),
                format="%(name)s")

# one session
db.define_table("plugin_pyodel_lecture",
                Field("template", "boolean", default=False),
                Field("chapter", "integer"),
                Field("name"),
                Field("course",
                      "reference plugin_pyodel_course"),
                Field("streams",
                      "list:reference plugin_pyodel_stream"),
                Field("description", "text",
                      comment=PLUGIN_PYODEL_MARKMIN_COMMENT), # MARKMIN
                Field("body", "text",
                      comment=PLUGIN_PYODEL_MARKMIN_COMMENT), # MARKMIN
                Field("by", "list:reference auth_user"),
                Field("documents", "list:reference wiki_page"),
                Field("tags", "list:string"),
                format="%(name)s")

db.define_table("plugin_pyodel_attendance",
                Field("student", "reference auth_user",
                default=auth.user_id),
                Field("course", "reference plugin_pyodel_course"),
                Field("paid", "double", default=0.0),
                Field("allowed", "boolean", default=False),
                Field("passed", "boolean", default=False),
                Field("score", "double"),
                format=plugin_pyodel_student_format
                )

db.define_table("plugin_pyodel_task",
                Field("template", "boolean", default=False),
                Field("name"),
                Field("body", "text",
                      comment=PLUGIN_PYODEL_MARKMIN_COMMENT), # MARKMIN
                Field("documents",
                "list:reference wiki_page"),
                Field("tags", "list:string"),
                Field("score", "double"),
                format="%(name)s")

db.define_table("plugin_pyodel_answer",
                Field("name"),
                Field("body", "text",
                      comment=PLUGIN_PYODEL_MARKMIN_COMMENT), # MARKMIN
                Field("tags", "list:string"),
                format="%(name)s"
                )

# Question can be multiple choice or not, or even an exercise,
# in which case it will probably not be an actual question
db.define_table("plugin_pyodel_question",
                Field("name"),
                Field("body", "text",
                      comment=PLUGIN_PYODEL_MARKMIN_COMMENT), # MARKMIN
                Field("tags", "list:string"),
                Field("score", "double"),
                Field("answers",
                      "list:reference plugin_pyodel_answer"),
                Field("correct",
                      "list:reference plugin_pyodel_answer",
                readable=False),
                Field("shuffle", "boolean", default=False),
                format="%(name)s"
                )

db.define_table("plugin_pyodel_test",
                Field("template", "boolean", default=False),
                Field("duration", "time"),
                Field("questions",
                      "list:reference plugin_pyodel_question"),
                Field("name"),
                Field("body", "text",
                      comment=PLUGIN_PYODEL_MARKMIN_COMMENT), # MARKMIN
                Field("tags", "list:string"),
                Field("shuffle", "boolean", default=False),
                format="%(name)s"
                )

db.define_table("plugin_pyodel_quiz",
                Field("body", "text"), # use quiz syntax
                Field("name"),
                Field("description", "text",
                      comment=PLUGIN_PYODEL_MARKMIN_COMMENT),
                Field("tags", "list:string"),
                Field("shuffle", "boolean"), # will mix questions, not answers
                Field("score", "double"),
                format="%(name)s")

# gradebook examination super-instances
# i.e. first midterm, second exam, final exam, ...
db.define_table("plugin_pyodel_instance",
                Field("name"),
                Field("abbreviation"),
                Field("ordered"), # A to Z (for spreadsheets)
                Field("formula"), # default formula for individual instances
                Field("replaces", "reference plugin_pyodel_instance"),
                format="%(name)s"
                )

db.define_table("plugin_pyodel_evaluation",
                Field("template", "boolean", default=False),
                Field("name"),
                Field("code"), # a letter or other identifier
                Field("description", "text",
                      comment=PLUGIN_PYODEL_MARKMIN_COMMENT), # MARKMIN
                Field("instance", "reference plugin_pyodel_instance"),
                Field("course",
                      "reference plugin_pyodel_course"),
                Field("lectures",
                      "list:reference plugin_pyodel_lecture"),
                Field("starts", "datetime"),
                Field("ends", "datetime"),
                Field("students",
                      "list:reference plugin_pyodel_attendance"),
                Field("evaluators",
                      "list:reference auth_user"),
                Field("tests", "list:reference plugin_pyodel_test"),
                Field("quizzes", "list:reference plugin_pyodel_quiz"),
                Field("score", "double"),
                Field("tags", "list:string"),
                Field("tasks", "list:reference plugin_pyodel_task"),
                format="%(name)s")

# Student's task work
db.define_table("plugin_pyodel_work",
                Field("body", "text",
                      comment=PLUGIN_PYODEL_MARKMIN_COMMENT), # MARKMIN
                Field("task", "reference plugin_pyodel_task"),
                Field("starts", "datetime"),
                Field("ends", "datetime"),
                Field("evaluation",
                      "reference plugin_pyodel_evaluation"),
                Field("documents",
                "list:reference wiki_page"),
                Field("score", "double"),
                format="%(task)s"
                )

# A timer for a test
db.define_table("plugin_pyodel_hourglass",
                Field("test", "reference plugin_pyodel_test"),
                Field("starts", "datetime"),
                Field("ends", "datetime"),
                Field("evaluation",
                      "reference plugin_pyodel_evaluation"),
                #Field("score", "double"),
                format="%(test)s")

# A timer for a quiz
db.define_table("plugin_pyodel_sandglass",
                Field("quiz", "reference plugin_pyodel_quiz"),
                Field("starts", "datetime"),
                Field("ends", "datetime"),
                Field("evaluation",
                      "reference plugin_pyodel_evaluation"),
                Field("score", "double"),
                Field("answers", "list:string"), # <int question>:<int answer> pairs
                format="%(quiz)s")

# A student's evaluation answer (can refer to an option
# or be redacted).
db.define_table("plugin_pyodel_retort",
                Field("hourglass",
                      "reference plugin_pyodel_hourglass"),
                Field("question",
                      "reference plugin_pyodel_question"),
                Field("answers",
                      "list:reference plugin_pyodel_answer"),
                # MARKMIN
                Field("body", "text",
                      comment=PLUGIN_PYODEL_MARKMIN_COMMENT),
                Field("score", "double"),
                format="%(answers)s"
               )

# gradebooks
db.define_table("plugin_pyodel_gradebook",
                Field("instances",
                      "list:reference plugin_pyodel_instance"), # which instances to show/compute
                Field("student", "reference auth_user"),
                Field("remarks", "text"),
                # format="%(student)s"
                format=plugin_pyodel_student_format)

def plugin_pyodel_grade_formula_compute(row):
    try:
        return db.plugin_pyodel_instance[row.instance].formula
    except (KeyError, ValueError, AttributeError):
        return None

# gradebook entries for filling a gradebook grid
db.define_table("plugin_pyodel_grade",
                Field("gradebook",
                      "reference plugin_pyodel_gradebook"),
                Field("score"), # A D, 10, 100%, Good , ...
                                # used for all course score
                Field("course",
                      "reference plugin_pyodel_course"),  # if not null,
                                                         # should override code,
                                                         # subject, name ...
                Field("signed", "datetime",
                      default=request.now,
                      writable=False),
                Field("authority",
                      "reference auth_user", default=auth.user_id),
                Field("instance",
                      "reference plugin_pyodel_instance"), # exam,
                                                           # practical work/activity.
                Field("signature", "upload"), # the authority signature copy
                Field("remarks", "text"),
                Field("formula", compute=plugin_pyodel_grade_formula_compute),
                                  # spreadsheet syntax (web2py spreadsheet.py)
                                  # references are plugin_pyodel_instance.abbreviation fields
                                  # i.e.: =fme+sme/2
                format="%(name)s"
                )


# Custom validators

db.plugin_pyodel_course.documents.requires = IS_IN_DB(db, \
'wiki_page.id', "%(slug)s", multiple=True)
db.plugin_pyodel_course.documents.represent = \
plugin_pyodel_show_documents
db.plugin_pyodel_course.body.represent = \
plugin_pyodel_show_markmin
db.plugin_pyodel_course.description.represent = \
plugin_pyodel_show_markmin

db.plugin_pyodel_lecture.documents.requires = IS_IN_DB(db, \
'wiki_page.id', "%(slug)s", multiple=True)
db.plugin_pyodel_lecture.documents.represent = \
plugin_pyodel_show_documents
db.plugin_pyodel_lecture.body.represent = plugin_pyodel_show_markmin
db.plugin_pyodel_lecture.description.represent = \
plugin_pyodel_show_markmin

db.plugin_pyodel_task.documents.requires = IS_IN_DB(db, \
'wiki_page.id', "%(slug)s", multiple=True)
db.plugin_pyodel_task.documents.represent = \
plugin_pyodel_show_documents
db.plugin_pyodel_task.body.represent = \
plugin_pyodel_show_markmin

db.plugin_pyodel_work.documents.requires = IS_IN_DB(db, \
'wiki_page.id', "%(slug)s", multiple=True)
db.plugin_pyodel_work.documents.represent = \
plugin_pyodel_show_documents
db.plugin_pyodel_work.body.represent = \
plugin_pyodel_show_markmin

db.plugin_pyodel_stream.body.represent = \
plugin_pyodel_show_markmin

db.plugin_pyodel_answer.body.represent = \
plugin_pyodel_show_markmin

db.plugin_pyodel_question.body.represent = \
plugin_pyodel_show_markmin

db.plugin_pyodel_test.body.represent = \
plugin_pyodel_show_markmin

db.plugin_pyodel_retort.body.represent = \
plugin_pyodel_show_markmin

db.plugin_pyodel_instance.ordered.requires = \
IS_IN_SET(PLUGIN_PYODEL_UPPERCASE_ALPHABET)

db.plugin_pyodel_instance.replaces.requires = \
IS_EMPTY_OR(IS_IN_DB(db, db.plugin_pyodel_instance, "%(name)s"))

db.plugin_pyodel_course.code.requires = \
IS_NOT_IN_DB(db, db.plugin_pyodel_course.code)

db.plugin_pyodel_evaluation.description.represent = \
plugin_pyodel_show_markmin

db.plugin_pyodel_quiz.description.represent = \
plugin_pyodel_show_markmin

response.files.append(URL(c="static", f="plugin_pyodel/pyodel.js"))

