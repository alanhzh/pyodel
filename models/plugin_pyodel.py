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


PLUGIN_PYODEL_MARKMIN_COMMENT=T("Use MARKMIN or plain text")
PLUGIN_PYODEL_UPPERCASE_ALPHABET = ["A", "B", "C", "D", "E",
                                    "F", "G", "H", "I", "J",
                                    "K", "L", "M", "N", "O",
                                    "P", "Q", "R", "S", "T",
                                    "U", "V", "W", "X", "Y",
                                    "Z"]

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
                Field("streams", "list:reference stream"),
                Field("body", "text",
                      comment=PLUGIN_PYODEL_MARKMIN_COMMENT), # MARKMIN
                Field("by", "list:reference auth_user"),
                Field("starts", "datetime"),
                Field("documents",
                      "list:reference plugin_wiki_page"), # STATIC PAGES
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
                Field("body", "text",
                      comment=PLUGIN_PYODEL_MARKMIN_COMMENT), # MARKMIN
                Field("by", "list:reference auth_user"),
                Field("documents", "list:reference plugin_wiki_page"),
                Field("tags", "list:string"),
                format="%(name)s")

db.define_table("plugin_pyodel_attendance",
                Field("student", "reference auth_user",
                default=auth.user_id),
                Field("course", "reference plugin_pyodel_course"),
                Field("paid", "double", default=0.0),
                Field("allowed", "boolean", default=False),
                Field("passed", default=False),
                Field("score", "double", default=0.0),
                format="%(student)s"
                )

db.define_table("plugin_pyodel_task",
                Field("template", "boolean", default=False),
                Field("name"),
                Field("body", "text",
                      comment=PLUGIN_PYODEL_MARKMIN_COMMENT), # MARKMIN
                Field("documents",
                "list:reference plugin_wiki_page"),
                Field("tags", "list:string"),
                Field("points", "double", default=0.0),
                format="%(name)s")

db.define_table("plugin_pyodel_answer",
                Field("body", "text",
                      comment=PLUGIN_PYODEL_MARKMIN_COMMENT), # MARKMIN
                Field("tags", "list:string"),
                format="%(body)s"
                )

# Question can be multiple choice or not, or even an exercise,
# in which case it will probably not be an actual question
db.define_table("plugin_pyodel_question",
                Field("body", "text",
                      comment=PLUGIN_PYODEL_MARKMIN_COMMENT), # MARKMIN
                Field("tags", "list:string"),
                Field("points", "double", default=0.0),
                Field("answers",
                      "list:reference plugin_pyodel_answer"),
                Field("correct",
                      "list:reference plugin_pyodel_answer",
                readable=False),
                Field("shuffle", "boolean", default=False),
                format="%(body)s"
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
                Field("description"),
                Field("tags", "list:string"),
                format="%(name)s")

# gradebook examination super-instances
# i.e. first midterm, second exam, final exam, ...
db.define_table("plugin_pyodel_instance",
                Field("name"),
                Field("abbreviation"),
                Field("ordered"), # A to Z (for spreadsheets)
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
                Field("score", "double", default=0.0),
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
                "list:reference plugin_wiki_page"),
                Field("points", "double", default=0.0),
                Field("score", "double", default=0.0),
                format="%(task)s"
                )

# A timer for a test
db.define_table("plugin_pyodel_hourglass",
                Field("test", "reference plugin_pyodel_test"),
                Field("starts", "datetime"),
                Field("ends", "datetime"),
                Field("evaluation",
                      "reference plugin_pyodel_evaluation"),
                Field("score", "double", default=0.0),
                format="%(test)s")

# A timer for a quiz
db.define_table("plugin_pyodel_sandglass",
                Field("quiz", "reference plugin_pyodel_quiz"),
                Field("starts", "datetime"),
                Field("ends", "datetime"),
                Field("evaluation",
                      "reference plugin_pyodel_evaluation"),
                Field("score", "double", default=0.0),
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
                Field("score", "double", default=0.0),
                format="%(answers)s"
               )

# gradebooks
db.define_table("plugin_pyodel_gradebook",
                Field("instances",
                      "list:reference plugin_pyodel_instance"), # which instances to show/compute
                Field("student", "reference auth_user"),
                Field("remarks", "text"),
                # format="%(student)s"
                format=lambda r: "%s %s (%s)" % \
                (db.auth_user[r.student].first_name,
                db.auth_user[r.student].last_name,
                r.student))

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
                Field("signed", "datetime"),
                Field("authority",
                      "reference auth_user"),
                Field("instance",
                      "reference plugin_pyodel_instance"), # exam,
                                                           # practical work/activity.
                Field("signature", "upload"), # the authority signature copy
                Field("remarks", "text"),
                Field("formula"), # spreadsheet syntax (web2py spreadsheet.py)
                                  # references are plugin_pyodel_instance.abbreviation fields
                                  # i.e.: =fme+sme/2
                format="%(name)s"
                )

###################################################################

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
                                   c="plugin_wiki",
                                   f="page",
                                   args=[item.slug,
                                   ]))) for item in value])
    else:
        return T("Empty")

# custom validators (to be declared after plugin_wiki)
def plugin_pyodel_configure_model():
    db.plugin_pyodel_course.documents.requires = IS_IN_DB(db, \
    "db.plugin_wiki_page", "%(slug)s", multiple=True)
    db.plugin_pyodel_course.documents.represent = \
    plugin_pyodel_show_documents
    db.plugin_pyodel_course.body.represent = \
    plugin_pyodel_show_markmin

    db.plugin_pyodel_lecture.documents.requires = IS_IN_DB(db, \
    "db.plugin_wiki_page", "%(slug)s", multiple=True)
    db.plugin_pyodel_lecture.documents.represent = \
    plugin_pyodel_show_documents
    db.plugin_pyodel_lecture.body.represent = plugin_pyodel_show_markmin

    db.plugin_pyodel_task.documents.requires = IS_IN_DB(db, \
    "db.plugin_wiki_page", "%(slug)s", multiple=True)
    db.plugin_pyodel_task.documents.represent = \
    plugin_pyodel_show_documents
    db.plugin_pyodel_task.body.represent = \
    plugin_pyodel_show_markmin

    db.plugin_pyodel_work.documents.requires = IS_IN_DB(db, \
    "db.plugin_wiki_page", "%(slug)s", multiple=True)
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

    db.plugin_pyodel_course.code.requires = \
    IS_NOT_IN_DB(db, db.plugin_pyodel_course.code)

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
