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

def index():
    return dict(message="hello from wizard.py")

def course():
    # create or edit a course
    # give the editor the option to
    # clone a pre-existent course
    course = None
    created = False
    if request.args(0) is None:
        new = True
        message=T("New course")
        form = SQLFORM.factory(db.course,
                               Field("clone",
                                     "reference course",
                                     requires=IS_EMPTY_OR(
                                         IS_IN_DB(
                                             db(db.course.template == True),
                                             db.course.id, "%(name)s")),
                                     default=None))
        if form.process().accepted:
            if form.vars.clone:
                lectures = db(db.lecture.course == form.vars.clone).select()
                cloned = db.course[form.vars.clone]
                form.vars.pop("clone")
                for key, value in cloned.as_dict().iteritems():
                    if (not form.vars.get(key)) and (not key == "id"):
                        form.vars[key] = value
                course = db.course.insert(**form.vars)
                for lecture in lectures:
                    new_lecture = lecture.as_dict()
                    new_lecture.pop("id")
                    new_lecture["course"] = lecture.course
                    db.lecture.insert(**new_lecture)
                response.flash = T("New course added")
                form = crud.read(db.course, course)
                created=True
    else:
        new = False
        course = request.args(0)
        form = SQLFORM(db.course, course)
        message=T("Update course") + " %s" % request.args(0)
        if form.process().accepted:
            response.flash = T("Course updated")
    return dict(message=message, form=form, new=new, created=created,
                course=course)

def lecture():
    # <url>new or lecture id/course id
    # expose (CRUD):
    # documents, streams, ...
    documents = None
    created = False
    new = False
    if request.args(0) == "new":
        new = True
        course = db.course[request.args(1)]
        db.lecture.course.readable = db.lecture.course.writable = False
        form = SQLFORM.factory(db.lecture,
                               Field("clone",
                                     "reference lecture",
                                     requires=IS_EMPTY_OR(
                                         IS_IN_DB(
                                             db(db.lecture.template == True),
                                             db.lecture.id, "%(name)s")),
                                     default=None))
        form.vars["course"] = course.id
        if form.process().accepted:
            if form.vars.clone:
                cloned = db.lecture[form.vars.clone]
                form.vars.pop("clone")
                for key, value in cloned.as_dict().iteritems():
                    if (not form.vars.get(key)) and (not key == "id"):
                        form.vars[key] = value
                lecture = db.lecture.insert(**form.vars)
                response.flash = T("New lecture added")
                form = crud.read(db.lecture, lecture)
                created = True
    elif request.args(0) is not None:
        lecture = db.lecture[request.args(0)]
        course = lecture.course
        db.lecture.course.writable = False
        form = SQLFORM(db.lecture, request.args(0))
    else:
        form = documents = created = new = course = None
    return dict(form=form, documents=documents, created=created, new=new,
                course=course)

# this functions should have this argument format:
# <url>/<number or new>/<what table>/<what record>

def task():
    return dict()

def quiz():
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
        form = SQLFORM.factory(Field("template", "reference quiz",
                                    requires = IS_EMPTY_OR(IS_IN_DB(db(db.quiz.template == True),
                                             db.quiz.id, "%(name)s")),
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
                tags_query = db.question.tags.contains(tag)
            else:
                tags_query |= db.question.tags.contains(tag)
                
        if tags_query is not None:
            db.quiz.questions.requires = IS_IN_DB(db(tags_query),
                                                      db.question.id,
                                                      "%(body)s",
                                                      multiple=True)
                                                      
        db.quiz.tags.writable = False
        db.quiz.tags.readable = False
        
        form = SQLFORM.factory(db.quiz,
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
            previous = db.quiz[session.quiz["quiz"]]
        elif session.quiz["template"]:
            previous = db.quiz[session.quiz["template"]]
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
                            myquery = db.question.tags.contains(phrase)
                        else:
                            myquery |= db.question.tags.contains(phrase)
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
                    session.quiz["quiz"] = db.quiz.insert(tags=tags, **form.vars)
                    
                session.quiz["new_questions"] = new_questions
                if not new_questions:
                    redirect(URL(f="quiz", args=["fifth",]))
                redirect(URL(f="quiz", args=["second",]))

    elif request.args(0) == "second":
        # no answers means need of redacted retort
        message = T("Second stage: type questions")
        question_fields = []
        quiz = db.quiz[session.quiz["quiz"]]

        answers_query = db.answer

        tags = None
        if not quiz.tags == []:
            tags = quiz.tags
            for x, tag in enumerate(tags):
                if x == 0:
                    answers_query = db.answer.tags.contains(tag)
                else:
                    answers_query |= db.answer.tags.contains(tag)

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
                                          db.answer.id,
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

                    question = db.question.insert(body=request.vars[k],
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
        quiz = db.quiz[session.quiz["quiz"]]
        # type answers in
        message = T("Third stage: type answers")
        answer_fields = []
        if quiz.tags == []:
            tags = None
        else:
            tags = quiz.tags
        for k, v in session.quiz["new_answers"].iteritems():
            question = db.question[k]
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
                    question = db.question[question]
                    
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
                question = db.question[k]
                if not len(v) <= 1:
                    answers = question.answers
                    if answers is None:
                        answers = list()
                    for body_tags in v:
                        answers.append(db.answer.insert(body=body_tags[0],
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
            question = db.question[number]
            if not question.answers in (None, []):
                if len(question.answers) > 1:
                    for x, answer in enumerate(question.answers):
                        if x == 0:
                            myset = db.answer.id == answer
                        else:
                            myset |= db.answer.id == answer
                    new_field = Field("question_%s_correct" % number,
                                                "list:reference answer",
                                                requires=IS_IN_DB(db(myset),
                                                                  db.answer.id,
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
                    question = db.question[q]
                    result = question.update_record(answers=v)
                    redirect(URL(f="quiz", args=["fifth",]))
        else:
            redirect(URL(f="quiz", args=["fifth",]))

    elif request.args(0) == "fifth":
        # allow to modify/set the answer's score
        # accept results or try again
        # allow to order question indexes
        quiz = db.quiz[session.quiz["quiz"]]
        if not quiz.questions in ([], None):
            fields = []
            for question in quiz.questions:
                question = db.question[question]
                fields.append(Field("question_%s_points" % question.id,
                                    "double", default=question.points,
                                    label=MARKMIN(question.body),
                                    comment=T("Points for this question")))
            form = SQLFORM.factory(*fields)
            message = T("Set the question scores")
            if form.process().accepted:
                for k, v in form.vars.iteritems():
                    question = db.question[k.split("_")[1]]
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

def evaluation():
    # one group/attendant
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
        form = SQLFORM(db.stream)
        if form.process().accepted:
            created = True
            stream = form.vars.id
            streams = referenced.streams
            if streams == None: streams = []
            streams.append(stream)
            referenced.update_record(streams=streams)
            form = crud.read(db.stream, stream)

    elif request.vars(0) is not None:
        stream = request.vars(0)
        form = crud.update(db.stream, request.vars(0))
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
    db.plugin_wiki_page.slug.writable = True
    db.plugin_wiki_page.slug.requires += (IS_NOT_EMPTY(),)
    if request.args(0) == "new":
        new = True
        form = SQLFORM(db.plugin_wiki_page)
        if form.process().accepted:
            documents = referenced.documents
            if documents == None: documents = []
            documents.append(form.vars.id)
            referenced.update_record(documents=documents)
            created = True
            document = form.vars.id
            form = crud.read(db.plugin_wiki_page, form.vars.id)
    elif request.args(0) is not None:
        document = request.args(0)
        form = crud.update(db.plugin_wiki_page, request.args(0))
    else:
        form = new = created = referenced = document = None

    return dict(form=form, new=new, created=created, referenced=referenced,
                document=document)




