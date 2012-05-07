# -*- coding: utf-8 -*-

# Pyodel: an e-learning multi-purpose tool for web2py
#    Copyright (C) 2012 Alan Etkin
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    * Web2py is Licensed under the LGPL license version 3
#    (http://www.gnu.org/licenses/lgpl.html)
#    Copyright (c) by Massimo Di Pierro (2007-2011)
#
#    contact: spametki@gmail.com


#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

import datetime

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    response.flash = "Welcome to web2py!"
    return dict(message=T('Hello World'))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())


########################################
## Unordered stuff (for demo purposes)
########################################

# users special panels
@auth.requires_membership("manager")
def manager():
    message=T("Manager panel")
    return dict(message=message)

@auth.requires_login()
def student():
    # attendance
    attendances = db(db.attendance.student == auth.user_id).select()
    courses_query = db.course.id < 0
    for attendance in attendances:
        courses_query |= db.course.id == attendance.course.id
    courses = db(courses_query).select()
    hourglasses = []
    deadlines = []
    for attendee in attendances:
        for row in db((db.hourglass.evaluation == db.evaluation.id) & \
                      (db.evaluation.students.contains(attendee.id))).select():
            hourglasses.append(row.hourglass)
        # retrieve deadlines and hourglasses
        for row in db((db.work.evaluation == db.evaluation.id) & \
                      (db.evaluation.students.contains(attendee.id))).select():
            deadlines.append(row.work)
    return dict(courses=courses, hourglasses=hourglasses, deadlines=deadlines)

@auth.requires(auth.has_membership(role="evaluator") or
    auth.has_membership(role="manager"))
def teacher():
    return dict()

# CRUD

def create():
    form = None
    table = request.args(0)
    if table is not None:
        form = crud.create(db[table])
        if form.process().accepted:
            response.flash = T("New %s created" % table)
    return dict(form=form)

def read():
    form = None
    table = request.args(0)
    if table is not None:
        form = crud.read(db[table])
    return dict(form=form)

def update():
    form = None
    table = request.args(0)
    record = request.args(1)
    if not None in (table, record):
        form = crud.update(db[table], int(record))
        if form.process().accepted:
            response.flash = T("%s updated" % table.capitalize())
    return dict(form=form)

def select():
    table = request.args(0)
    if not table in db.tables():
        raise HTTP(400, "Incorrect select request")
    query, args = db[table], request.args[:1]
    return dict(query=query, args=args, table=table)


@auth.requires_login()
def evaluate():
    # create a hourglass from
    # a given evaluation
    evaluation = int(request.args(1))
    quiz = int(request.args(3))
    hourglass = db.hourglass.insert(evaluation=evaluation,
                                    quiz=quiz,
                                    starts=request.now,
                                    ends=request.now + \
                                    datetime.timedelta(minutes=120))
    # create a link to the quiz
    message = DIV(H3(T("A new quiz exam has been created")),
                  H5(SPAN(T("You can start it")),
                     SPAN(A(T("here"),
                            _href=URL(f="quiz",
                                      args=["hourglass",
                                            hourglass])))))
    return dict(message=message)

def evaluation():
    evaluation = db.evaluation[request.args(1)]
    quizes = UL(*[LI(A(quiz.name,
                       _href=URL(f="evaluate",
                                 args=["evaluation",
                                       evaluation.id,
                                       "quiz",
                                       quiz.id]
                                )
                       )) for quiz in evaluation.quizes])
    return dict(quizes=quizes)

def quiz():
    # quiz panel:
    # quiz data
    hourglass = db.hourglass[int(request.args(1))]
    quiz = hourglass.quiz
    # show time
    # questions list (show answer if any)
    # link to answer edition
    questions_query = db.question.id == 0
    for question in quiz.questions:
        questions_query |= db.question.id == question
    questions = SQLTABLE(db(questions_query).select(),
                         linkto=lambda field, type, ref: \
                         URL(f="answer",
                             args=["hourglass",
                                   hourglass.id,
                                   "question",
                                   field]))
    retorts = hourglass.retort.select()
    if hourglass.ends > request.now:
        left = LOAD(c="default",
                          f="left",
                          extension="load",
                          args=["hourglass", hourglass.id],
                          timeout=10000,
                          ajax=True,
                          times="infinity")
    else:
        left = T("The exam is finished.")
    return dict(hourglass=hourglass, quiz=quiz,
                questions=questions, retorts=retorts,
                left=left)

def answer():
    # write retort or choose the correct form
    # link to back to the quiz panel
    # show time
    
    hourglass = db.hourglass[request.args(1)]
    question = db.question[request.args(3)]
    multiple = False
    new = False
    choice = None
    message = None
    previous = next = None

    if None in (hourglass, question):
        raise HTTP(500, T("No quiz or question selected."))

    quiz = hourglass.quiz
    questions = quiz.questions

    answers_query = db.answer.id == 0
    for answer in question.answers:
        answers_query |= db.answer.id == answer
        
    retort = db((db.retort.question == question.id) & \
                (db.retort.hourglass == hourglass.id)
                ).select().first()
                
    answers = db(answers_query).select()

    if len(answers) > 0:
        # a multiple choice question
        multiple = True

    if retort is None:
        retort_id = db.retort.insert(hourglass=hourglass.id,
                                     question=question.id)
        retort = db.retort[retort_id]
        new = True

    marked = []
    if retort.answers is not None:
        for answer in answers:
            if answer.id in retort.answers:
                marked.append(answer.id)

    if multiple:
        fields = [Field("answer_%s" % answer.id,
                         "boolean",
                         label=None,
                         comment=MARKMIN(answer.body),
                         default=answer.id in marked) for \
                         answer in answers]
    else:
        if retort.body is not None:
            body = retort.body
        else:
            body = ""
        fields = [Field("body",
                        "text",
                        default=body,
                        comment=markmin_comment),]

    if hourglass.ends > request.now:
        form = SQLFORM.factory(*fields)
        if form.process(keepvalues=True).accepted:
            multivalues = []
            if multiple:
                for k, v in form.vars.iteritems():
                    if k.startswith("answer_") and v:
                        multivalues.append(int(k.split("_")[1]))
                retort.update_record(answers=multivalues)
            else:
                retort.update_record(body=form.vars.body)

        left = LOAD(c="default",
                    f="left",
                    extension="load",
                    args=["hourglass", hourglass.id],
                    timeout=10000,
                    ajax=True,
                    times="infinity")

    else:
        left = T("The exam is finished.")
        form = SQLFORM.factory(*fields, readonly=True)

    try:
        if not questions.index(question.id) == 0:
            previous = A(T("Previous"), _href=URL(f="answer",
                           args=["hourglass",
                                 hourglass.id,
                                 "question",
                                 questions[questions.index(
                                     question.id) -1]]))
        else:
            previous = None
    except IndexError:
        previous = None

    try:
        next = A(T("Next"), _href=URL(f="answer",
                       args=["hourglass",
                             hourglass.id,
                             "question",
                             questions[questions.index(
                                           question.id) +1]]))
    except IndexError:
        next = None

    return dict(previous=previous, next=next, form=form,
                question=MARKMIN(question.body),
                quiz=A(T("Back to the quiz panel"),
                       _href=URL(f="quiz",
                                 args=["hourglass",
                                       hourglass.id])),
                left=left)

def checkout():
    # show score if possible and
    # thank the user
    return dict(message=T("Not implemented."))

@auth.requires_login()
def apply():

    # sign if for a course
    course = db.course[request.args(1)]
    attendance = db.attendance.insert(course=course.id,
                                      allowed=True,
                                      student=auth.user_id)
    
    # does the student have evaluations?
    db.evaluation.insert(course=course.id,
                         students=[attendance,],
                         name=course.name,
                         starts=request.now,
                         ends=request.now + datetime.timedelta(hours=12),
                         quizes=[quiz.id for quiz in db(db.quiz).select()])
    
    message = T("You have been signed as attendee to the %s course.") % course.name
    return dict(message=message, course=course)
    
@auth.requires_login()
def course():
    # show the course to the attendee
    course = db.course[request.args(1)]
    attendee = db((db.attendance.student == auth.user_id) & \
                    (db.attendance.course == course.id)).select().first()
    rows = db((db.evaluation.students.contains(attendee.id)) & \
              (db.evaluation.course == course.id)).select()
    evaluations = SQLTABLE(rows, linkto=URL(f="evaluation"))
    return dict(course=course, evaluations=evaluations)

@auth.requires_login()
def courses():
    # show taken and not taken courses
    query = db.course.id > 0
    courses = [attendance.course for attendance in \
               db(db.attendance.student == auth.user_id).select()]
    for course in courses:
        query &= db.course.id != course
    untaken = SQLTABLE(db(query).select("course.id",
                                        "course.code",
                                        "course.name",
                                        "course.starts"),
                       linkto=URL(f="apply"))
    taken = SQLTABLE(db(~query).select("course.id",
                                       "course.code",
                                       "course.name",
                                       "course.starts"),
                     linkto=URL(f="course"))
    return dict(taken=taken, untaken=untaken)

def left():
    event = db[request.args(0)][request.args(1)]
    left = event.ends - request.now
    return dict(left=left)
