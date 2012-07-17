# -*- coding: utf-8 -*-

# Pyodel App: an e-learning multi-purpose tool for web2py
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
    response.flash = "Welcome to plugin_pyodel!"
    return dict(message=T('Hollehri du dödle dirh!'))

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
    attendances = db(db.plugin_pyodel_attendance.student == auth.user_id).select()
    courses_query = db.plugin_pyodel_course.id < 0
    for attendance in attendances:
        courses_query |= db.plugin_pyodel_course.id == attendance.course.id
    courses = db(courses_query).select()
    hourglasses = []
    deadlines = []
    for attendee in attendances:
        for row in db((db.plugin_pyodel_hourglass.evaluation == db.plugin_pyodel_evaluation.id) & \
                      (db.plugin_pyodel_evaluation.students.contains(attendee.id))).select():
            hourglasses.append(row.hourglass)
        # retrieve deadlines and hourglasses
        for row in db((db.plugin_pyodel_work.evaluation == db.plugin_pyodel_evaluation.id) & \
                      (db.plugin_pyodel_evaluation.students.contains(attendee.id))).select():
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
    hourglass = db.plugin_pyodel_hourglass.insert(evaluation=evaluation,
                                    quiz=quiz,
                                    starts=request.now,
                                    ends=request.now + \
                                    datetime.timedelta(minutes=120))
    # create a link to the quiz
    message = DIV(H3(T("A new quiz exam has been created")),
                  H5(SPAN(T("You can start it")),
                     SPAN(A(T("here"),
                            _href=URL(f="quiz",
                                      args=["plugin_pyodel_hourglass",
                                            hourglass])))))
    return dict(message=message)

def evaluation():
    evaluation = db.plugin_pyodel_evaluation[request.args(1)]
    quizes = UL(*[LI(A(quiz.name,
                       _href=URL(f="evaluate",
                                 args=["plugin_pyodel_evaluation",
                                       evaluation.id,
                                       "plugin_pyodel_quiz",
                                       quiz.id]
                                )
                       )) for quiz in evaluation.quizes])
    return dict(quizes=quizes)


def quiz():
    # quiz panel:
    # quiz data
    hourglass = db.plugin_pyodel_hourglass[int(request.args(1))]
    quiz = hourglass.quiz
    # show time
    # questions list (show answer if any)
    # link to answer edition
    questions_query = db.plugin_pyodel_question.id == 0
    for question in quiz.questions:
        questions_query |= db.plugin_pyodel_question.id == question
    questions = SQLTABLE(db(questions_query).select(),
                         linkto=lambda field, type, ref: \
                         URL(f="answer",
                             args=["plugin_pyodel_hourglass",
                                   hourglass.id,
                                   "plugin_pyodel_question",
                                   field]))
    retorts = hourglass.retort.select()
    if hourglass.ends > request.now:
        left = LOAD(c="default",
                          f="left",
                          extension="load",
                          args=["plugin_pyodel_hourglass", hourglass.id],
                          timeout=10000,
                          ajax=True,
                          times="infinity")
    else:
        left = T("The exam is finished.")
    return dict(hourglass=hourglass, quiz=quiz,
                questions=questions, retorts=retorts,
                left=left)

#########################################################################
# start of quiz()
#########################################################################

def quiz_wizard():
    # <url>/step n/

    # TODO: step zero: choose a quiz template
    session.quiz = session.get("quiz", {"template": None,
                                        "new_questions": 0,
                                        "auto": [],
                                        "message": "",
                                        "new_answers": {},
                                        "quiz": None,
                                        "choose_correct": set(),
                                        "tags": set()})
    if request.args(0) is None:
        message = T("Start: choose a template")
        form = SQLFORM.factory(Field("template", "reference plugin_pyodel_quiz",
                                    requires = IS_EMPTY_OR(IS_IN_DB(db(db.plugin_pyodel_quiz.template == True),
                                             db.plugin_pyodel_quiz.id, "%(name)s")),
                                             comment=T("Choose a template or leave blank for new")),
                               Field("tags", "list:string", comment=T("Insert tags (Enter adds a new tag)")))
        if form.process().accepted:
            if form.vars.template:
                session.quiz["template"] = form.vars.template
            if form.vars.tags:
                if isinstance(form.vars.tags, basestring):
                    session.quiz["tags"] = set([form.vars.tags,])
                else:
                    session.quiz["tags"] = set(form.vars.tags)
            redirect(URL(f="quiz", args=["first",]))

    elif request.args(0) == "clear":
        session.quiz = None
        redirect(URL(f="quiz"))

    elif request.args(0) == "first":
        message = T("First stage: options")
        tags_query = None
        for x, tag in enumerate(session.quiz["tags"]):
            if x == 0:
                tags_query = db.plugin_pyodel_question.tags.contains(tag)
            else:
                tags_query |= db.plugin_pyodel_question.tags.contains(tag)

        if tags_query is not None:
            db.plugin_pyodel_quiz.questions.requires = IS_IN_DB(db(tags_query),
                                                      db.plugin_pyodel_question.id,
                                                      "%(body)s",
                                                      multiple=True)

        db.plugin_pyodel_quiz.tags.writable = False
        db.plugin_pyodel_quiz.tags.readable = False

        form = SQLFORM.factory(db.plugin_pyodel_quiz,
                               Field("new_questions",
                                     "integer",
                                     default=0,
                                     comment=T("Number of new questions for this quiz")),
                               Field("auto", "text",
                                     label=T("I want") + "...",
                                     comment=XML("%s<br/>2 yodel, doodle, du<br/>3 dö, yodel<br/>&lt;%s&gt;" %
                                                 (T("Try something like"),
                                                  T("Quantity followed by comma separated tags")))),
                               Field("show_auto",
                                     "boolean",
                                     default=False,
                                     comment=T("Show auto selection before proceeding. Uncheck to continue")
                               ))
        previous = None
        if session.quiz["quiz"]:
            previous = db.plugin_pyodel_quiz[session.quiz["quiz"]]
        elif session.quiz["template"]:
            previous = db.plugin_pyodel_quiz[session.quiz["template"]]
        if previous is not None:
            form.vars.body = previous.body

            if not previous.tags in (None, []):
                if isinstance(previous.tags, list):
                    for tag in previous.tags:
                        print "adding the tag %s to the session tags set" % tag
                        session.quiz["tags"].add(tag)

            form.vars.name = previous.name
            form.vars.duration = previous.duration
            form.vars.questions = previous.questions
            form.vars.shuffle = previous.shuffle

        if form.process(keepvalues=True).accepted:
            # create a quiz
            new_questions = form.vars.new_questions
            if new_questions in (None, ""):
                new_questions = 0
            auto = form.vars.auto
            show_auto = form.vars.show_auto
            auto_questions = set()
            if form.vars.auto:
                auto_lines = form.vars.auto.splitlines()
                for line in auto_lines:
                    if not line:
                        break
                    phrases = [phrase for phrase in line.split(",")]
                    first = phrases[0]
                    number = int(first.split(" ")[0])
                    words = first.split(" ")[1]
                    # words = " ".join(words)
                    if len(phrases) > 1:
                        phrases.pop(0)
                        phrases.insert(0, words)
                    else:
                        phrases = [words,]
                    for x, phrase in enumerate(phrases):
                        if x == 0:
                            myquery = db.plugin_pyodel_question.tags.contains(phrase)
                        else:
                            myquery |= db.plugin_pyodel_question.tags.contains(phrase)
                    myrows = db(myquery).select(orderby="<random>")
                    for x, row in enumerate(myrows):
                        if x < number:
                            auto_questions.add(row.id)
                auto_questions = list(auto_questions)

            # TODO: add manually selected questions and erease the form's
            # I want... content to avoid re-processing of the query. Filter
            # redundant items with set()

            if form.vars.show_auto:
                form.custom.widget.auto[0] = ""
                if auto_questions:
                    # The following doesn't update selections
                    # form.vars.questions = auto_questions
                    for option in form.custom.widget.questions.elements("option"):
                        if int(option["_value"]) in auto_questions:
                            option["_selected"] = "selected"

            else:
                # TODO: add auto field questions or
                # confirm on input
                form.vars.pop("new_questions")
                form.vars.pop("auto")
                form.vars.pop("show_auto")

                if len(session.quiz["tags"]) > 0:
                    tags = list(session.quiz["tags"])
                    print "Pre-form tags", tags
                else:
                    tags = None

                if session.quiz["quiz"]:
                    previous.update_record(tags=tags, **form.vars)
                else:
                    session.quiz["quiz"] = db.plugin_pyodel_quiz.insert(tags=tags, **form.vars)

                session.quiz["new_questions"] = new_questions
                if not new_questions:
                    redirect(URL(f="quiz", args=["fifth",]))
                redirect(URL(f="quiz", args=["second",]))

    elif request.args(0) == "second":
        # no answers means need of redacted retort
        message = T("Second stage: type questions")
        question_fields = []
        quiz = db.plugin_pyodel_quiz[session.quiz["quiz"]]

        answers_query = db.plugin_pyodel_answer

        tags = None
        if not quiz.tags == []:
            tags = quiz.tags
            for x, tag in enumerate(tags):
                if x == 0:
                    answers_query = db.plugin_pyodel_answer.tags.contains(tag)
                else:
                    answers_query |= db.plugin_pyodel_answer.tags.contains(tag)

        for x in range(session.quiz["new_questions"]):
            x += 1
            question_fields.append(Field("question_%s" % x,
                                          writable=False,
                                          default=H3("Question %s" % int_to_roman(x)),
                                          label=""))
            question_fields.append(Field("question_%s_body" % x,
                                          "text",
                                          label=T("Body")))
            question_fields.append(Field("question_%s_tags" % x,
                                         "list:string", default=tags,
                                          label=T("Tags")))
            question_fields.append(Field("question_%s_answers" % x,
                                          "list:reference answer",
                                          requires=IS_IN_DB(db(answers_query),
                                          db.plugin_pyodel_answer.id,
                                          "%(body)s",
                                          multiple=True),
                                          label=T("Answers")))
            question_fields.append(Field("question_%s_shuffle" % x,
                                          "boolean",
                                          label=T("Shuffle")))
            question_fields.append(Field("question_%s_new_answers" % x,
                                          "integer",
                                          label=T("New answers")))

        # forget new questions
        session.quiz["new_questions"] = 0
        form = SQLFORM.factory(*question_fields)
        questions = []
        if form.process().accepted:
            # create questions if addressed and add to the quiz list
            for k, v in request.vars.iteritems():
                if k.startswith("question_") and k.endswith("_body") and v:
                    number = int(k.split("_")[1])
                    if not request.vars["question_%s_tags"] in (None, "", []):
                        tags = request.vars["question_%s_tags" % number]
                    else:
                        tags = None
                    shuffle = request.vars["question_%s_shuffle" % number]
                    answers = request.vars["question_%s_answers" % number]

                    question = db.plugin_pyodel_question.insert(body=request.vars[k],
                                                  tags=tags,
                                                  shuffle=shuffle,
                                                  answers=answers)
                    questions.append(question)
                    if request.vars["question_%s_new_answers" % number]:
                        session.quiz["new_answers"][question] = \
                            request.vars["question_%s_new_answers" % number]

            if not quiz.questions in (None, "", []):
                row_questions = set(quiz.questions)
            else:
                row_questions = set()
            for question in questions: row_questions.add(question)
            quiz.update_record(questions=list(row_questions))
            redirect(URL(f="quiz", args=["third",]))

    elif request.args(0) == "third":
        quiz = db.plugin_pyodel_quiz[session.quiz["quiz"]]
        # type answers in
        message = T("Third stage: type answers")
        answer_fields = []
        if quiz.tags == []:
            tags = None
        else:
            tags = quiz.tags
        for k, v in session.quiz["new_answers"].iteritems():
            question = db.plugin_pyodel_question[k]
            v = int(v)
            if v > 0:
                answer_fields.append(Field("question_%s" % k,
                                           writable=False,
                                           label=None,
                                           default=MARKMIN(question.body)
                                           ))
                for x in range(v):
                    x += 1
                    answer_fields.append(Field("answer_%s_%s_body" % (k, x),
                                               "text",
                                               label=T("Body for %s") % int_to_roman(x)))
                    answer_fields.append(Field("answer_%s_%s_tags" % (k, x),
                                               "list:string",
                                               label=T("Tags for %s") % int_to_roman(x),
                                               default=tags))

        # TODO: fix redundant question/answer session object updates
        form = SQLFORM.factory(*answer_fields)
        if form.process().accepted:

            answers = dict()
            data = dict()

            for k in request.vars:
                if k.startswith("answer_") and k.endswith("body"):
                    question, answer = int(k.split("_")[1]), int(k.split("_")[2])
                    question = db.plugin_pyodel_question[question]

                    if not answers.has_key(question.id):
                        answers[question.id] = set()
                        data[question.id] = list()

                    tags = None
                    body = None

                    body = request.vars["answer_%s_%s_body" % (question.id, answer)]
                    tags = request.vars["answer_%s_%s_tags" % (question.id, answer)]

                    if body is not None:
                        if tags == []:
                            tags = None
                        data[question.id].append((body, tags))

            for k, v in data.iteritems():
                question = db.plugin_pyodel_question[k]
                if not len(v) <= 1:
                    answers = question.answers
                    if answers is None:
                        answers = list()
                    for body_tags in v:
                        answers.append(db.plugin_pyodel_answer.insert(body=body_tags[0],
                                       tags=body_tags[1]))
                    question.update_record(answers=answers)
                    session.quiz["choose_correct"].add(question.id)

            # forget new answers
            session.quiz["new_answers"] = {}
            redirect(URL(f="quiz", args=["fourth"]))

    elif request.args(0) == "fourth":
        # ask for correct answers for the new questions
        message = T("Mark the correct answers")
        choose_correct = session.quiz["choose_correct"]
        correct_fields = []
        for number in choose_correct:
            myset = None
            question = db.plugin_pyodel_question[number]
            if not question.answers in (None, []):
                if len(question.answers) > 1:
                    for x, answer in enumerate(question.answers):
                        if x == 0:
                            myset = db.plugin_pyodel_answer.id == answer
                        else:
                            myset |= db.plugin_pyodel_answer.id == answer
                    new_field = Field("question_%s_correct" % number,
                                                "list:reference answer",
                                                requires=IS_IN_DB(db(myset),
                                                                  db.plugin_pyodel_answer.id,
                                                                  "%(body)s",
                                                                  multiple=True))
                    correct_fields.append(Field("question_%s" % number,
                                                writable=False,
                                                default=MARKMIN(question.body)
                                                ))
                    correct_fields.append(new_field)
        if len(correct_fields) > 0:
            form = SQLFORM.factory(*correct_fields)
            if form.process().accepted:
                for k, v in form.vars.iteritems():
                    q = k.split("_")[1]
                    question = db.plugin_pyodel_question[q]
                    result = question.update_record(answers=v)
                    redirect(URL(f="quiz", args=["fifth",]))
        else:
            redirect(URL(f="quiz", args=["fifth",]))

    elif request.args(0) == "fifth":
        # allow to modify/set the answer's score
        # accept results or try again
        # allow to order question indexes
        quiz = db.plugin_pyodel_quiz[session.quiz["quiz"]]
        if not quiz.questions in ([], None):
            fields = []
            for question in quiz.questions:
                question = db.plugin_pyodel_question[question]
                fields.append(Field("question_%s_points" % question.id,
                                    "double", default=question.points,
                                    label=MARKMIN(question.body),
                                    comment=T("Points for this question")))
            form = SQLFORM.factory(*fields)
            message = T("Set the question scores")
            if form.process().accepted:
                for k, v in form.vars.iteritems():
                    question = db.plugin_pyodel_question[k.split("_")[1]]
                    result = question.update_record(points=v)
                redirect(URL(f="quiz", args=["sixth",]))
        else:
            form = None
            message = T("No questions found for this quiz")
    elif request.args(0) == "sixth":
        form = None
        message = T("The quiz finished sucessfully")
    else:
        form = message = None
    return dict(form=form, message=message)

####################################################################################
# end of quiz()
####################################################################################


def answer():
    # write retort or choose the correct form
    # link to back to the quiz panel
    # show time

    hourglass = db.plugin_pyodel_hourglass[request.args(1)]
    question = db.plugin_pyodel_question[request.args(3)]
    multiple = False
    new = False
    choice = None
    message = None
    previous = next = None

    if None in (hourglass, question):
        raise HTTP(500, T("No quiz or question selected."))

    quiz = hourglass.quiz
    questions = quiz.questions

    answers_query = db.plugin_pyodel_answer.id == 0
    for answer in question.answers:
        answers_query |= db.plugin_pyodel_answer.id == answer

    retort = db((db.plugin_pyodel_retort.question == question.id) & \
                (db.plugin_pyodel_retort.hourglass == hourglass.id)
                ).select().first()

    answers = db(answers_query).select()

    if len(answers) > 0:
        # a multiple choice question
        multiple = True

    if retort is None:
        retort_id = db.plugin_pyodel_retort.insert(hourglass=hourglass.id,
                                     question=question.id)
        retort = db.plugin_pyodel_retort[retort_id]
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
                           args=["plugin_pyodel_hourglass",
                                 hourglass.id,
                                 "plugin_pyodel_question",
                                 questions[questions.index(
                                     question.id) -1]]))
        else:
            previous = None
    except IndexError:
        previous = None

    try:
        next = A(T("Next"), _href=URL(f="answer",
                       args=["plugin_pyodel_hourglass",
                             hourglass.id,
                             "plugin_pyodel_question",
                             questions[questions.index(
                                           question.id) +1]]))
    except IndexError:
        next = None

    return dict(previous=previous, next=next, form=form,
                question=MARKMIN(question.body),
                quiz=A(T("Back to the quiz panel"),
                       _href=URL(f="quiz",
                                 args=["plugin_pyodel_hourglass",
                                       hourglass.id])),
                left=left)

def checkout():
    # show score if possible and
    # thank the user
    return dict(message=T("Not implemented."))

@auth.requires_login()
def apply():

    # sign if for a course
    course = db.plugin_pyodel_course[request.args(1)]
    attendance = db.plugin_pyodel_attendance.insert(course=course.id,
                                      allowed=True,
                                      student=auth.user_id)

    # does the student have evaluations?
    db.plugin_pyodel_evaluation.insert(course=course.id,
                         students=[attendance,],
                         name=course.name,
                         starts=request.now,
                         ends=request.now + datetime.timedelta(hours=12),
                         quizzes=[quiz.id for quiz in db(db.plugin_pyodel_quiz).select()])

    message = T("You have been signed as attendee to the %s course.") % course.name
    return dict(message=message, course=course)

@auth.requires_login()
def course():
    # show the course to the attendee
    course = db.plugin_pyodel_course[request.args(1)]
    attendee = db((db.plugin_pyodel_attendance.student == auth.user_id) & \
                    (db.plugin_pyodel_attendance.course == course.id)).select().first()
    rows = db((db.plugin_pyodel_evaluation.students.contains(attendee.id)) & \
              (db.plugin_pyodel_evaluation.course == course.id)).select()
    evaluations = SQLTABLE(rows, linkto=URL(f="evaluation"))
    return dict(course=course, evaluations=evaluations)


def course_wizard():
    # create or edit a course
    # give the editor the option to
    # clone a pre-existent course
    course = None
    created = False
    if request.args(0) is None:
        new = True
        message=T("New course")
        form = SQLFORM.factory(db.plugin_pyodel_course,
                               Field("clone",
                                     "reference plugin_pyodel_course",
                                     requires=IS_EMPTY_OR(
                                         IS_IN_DB(
                                             db(db.plugin_pyodel_course.template == True),
                                             db.plugin_pyodel_course.id, "%(name)s")),
                                     default=None))
        if form.process().accepted:
            if form.vars.clone:
                lectures = db(db.plugin_pyodel_lecture.course == form.vars.clone).select()
                cloned = db.plugin_pyodel_course[form.vars.clone]
                form.vars.pop("clone")
                for key, value in cloned.as_dict().iteritems():
                    if (not form.vars.get(key)) and (not key == "id"):
                        form.vars[key] = value
                course = db.plugin_pyodel_course.insert(**form.vars)
                for lecture in lectures:
                    new_lecture = lecture.as_dict()
                    new_lecture.pop("id")
                    new_lecture["course"] = lecture.course
                    db.plugin_pyodel_lecture.insert(**new_lecture)
                response.flash = T("New course added")
                form = crud.read(db.plugin_pyodel_course, course)
                created=True
    else:
        new = False
        course = request.args(0)
        form = SQLFORM(db.plugin_pyodel_course, course)
        message=T("Update course") + " %s" % request.args(0)
        if form.process().accepted:
            response.flash = T("Course updated")
    return dict(message=message, form=form, new=new, created=created,
                course=course)


@auth.requires_login()
def courses():
    # show taken and not taken courses
    query = db.plugin_pyodel_course.id > 0
    courses = [attendance.course for attendance in \
               db(db.plugin_pyodel_attendance.student == auth.user_id).select()]
    for course in courses:
        query &= db.plugin_pyodel_course.id != course
    untaken = SQLTABLE(db(query).select("plugin_pyodel_course.id",
                                        "plugin_pyodel_course.code",
                                        "plugin_pyodel_course.name",
                                        "plugin_pyodel_course.starts"),
                       linkto=URL(f="apply"))
    taken = SQLTABLE(db(~query).select("plugin_pyodel_course.id",
                                       "plugin_pyodel_course.code",
                                       "plugin_pyodel_course.name",
                                       "plugin_pyodel_course.starts"),
                     linkto=URL(f="course"))
    return dict(taken=taken, untaken=untaken)

def left():
    event = db[request.args(0)][request.args(1)]
    left = event.ends - request.now
    return dict(left=left)


def lecture():
    # <url>new or lecture id/course id
    # expose (CRUD):
    # documents, streams, ...
    documents = None
    created = False
    new = False
    if request.args(0) == "new":
        new = True
        course = db.plugin_pyodel_course[request.args(1)]
        db.plugin_pyodel_lecture.course.readable = db.plugin_pyodel_lecture.course.writable = False
        form = SQLFORM.factory(db.plugin_pyodel_lecture,
                               Field("clone",
                                     "reference plugin_pyodel_lecture",
                                     requires=IS_EMPTY_OR(
                                         IS_IN_DB(
                                             db(db.plugin_pyodel_lecture.template == True),
                                             db.plugin_pyodel_lecture.id, "%(name)s")),
                                     default=None))
        form.vars["course"] = course.id
        if form.process().accepted:
            if form.vars.clone:
                cloned = db.plugin_pyodel_lecture[form.vars.clone]
                form.vars.pop("clone")
                for key, value in cloned.as_dict().iteritems():
                    if (not form.vars.get(key)) and (not key == "id"):
                        form.vars[key] = value
                lecture = db.plugin_pyodel_lecture.insert(**form.vars)
                response.flash = T("New lecture added")
                form = crud.read(db.plugin_pyodel_lecture, lecture)
                created = True
    elif request.args(0) is not None:
        lecture = db.plugin_pyodel_lecture[request.args(0)]
        course = lecture.course
        db.plugin_pyodel_lecture.course.writable = False
        form = SQLFORM(db.plugin_pyodel_lecture, request.args(0))
    else:
        form = documents = created = new = course = None
    return dict(form=form, documents=documents, created=created, new=new,
                course=course)

# this functions should have this argument format:
# <url>/<number or new>/<what table>/<what record>

def task():
    return dict()


def evaluations():
    # <url>/new or id/course id
    # paced multi-attendant, evaluation creator

    # first step: use or create an evaluation header template

    # second step: ¿clone quizzes? or give create access

    return dict()

def tasks():
    # <url>/new or id/course id
    # paced multi-attendant, task creator

    # first step: use or create an task header template

    # second step: ¿clone quizzes? or give create access

    return dict()

def stream():
    # <url>/new or id/table/id
    new = False
    created = False
    referenced = stream = None
    referenced = db[request.args(1)][request.args(2)]
    if request.vars(0) == "new":
        new = True
        form = SQLFORM(db.plugin_pyodel_stream)
        if form.process().accepted:
            created = True
            stream = form.vars.id
            streams = referenced.streams
            if streams == None: streams = []
            streams.append(stream)
            referenced.update_record(streams=streams)
            form = crud.read(db.plugin_pyodel_stream, stream)

    elif request.vars(0) is not None:
        stream = request.vars(0)
        form = crud.update(db.plugin_pyodel_stream, request.vars(0))
    else:
        form = None
    return dict(form=form, created=created, new=new, referenced=referenced, stream=stream)

def document():
    # url parameters
    # id or new/referenced table/id
    # example:
    # New document for the course with id 1
    # <url>/new/course/1

    new = False
    created = False
    referenced = db[request.args(1)][request.args(2)]
    document = None
    db.plugin_pyodel_plugin_wiki_page.slug.writable = True
    db.plugin_pyodel_plugin_wiki_page.slug.requires += (IS_NOT_EMPTY(),)
    if request.args(0) == "new":
        new = True
        form = SQLFORM(db.plugin_pyodel_plugin_wiki_page)
        if form.process().accepted:
            documents = referenced.documents
            if documents == None: documents = []
            documents.append(form.vars.id)
            referenced.update_record(documents=documents)
            created = True
            document = form.vars.id
            form = crud.read(db.plugin_pyodel_plugin_wiki_page, form.vars.id)
    elif request.args(0) is not None:
        document = request.args(0)
        form = crud.update(db.plugin_pyodel_plugin_wiki_page, request.args(0))
    else:
        form = new = created = referenced = document = None

    return dict(form=form, new=new, created=created, referenced=referenced,
                document=document)

def sandglass():
    return dict()
