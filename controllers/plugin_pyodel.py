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

####################################################################
############### Plugin controller local functions ##################
####################################################################
import datetime

def even_or_odd(x):
    eoo = "odd"
    is_even = int(x) % 2 == 0
    if is_even:
        eoo = "even"
    return eoo

####################################################################
######################### Plugin components ########################
####################################################################

@auth.requires_membership(role="manager")
def grid():
    """ grid/table/tablename """
    db.plugin_pyodel_sandglass.feedback.readable = \
    db.plugin_pyodel_sandglass.feedback.writable = \
    db.plugin_pyodel_hourglass.feedback.readable = \
    db.plugin_pyodel_hourglass.feedback.writable = True
    table = request.args[1]
    return dict(grid=SQLFORM.smartgrid(db[table], args=request.args[:2]),
                back=A("Back to panel", _href=URL(f="panel")))

@auth.requires_membership(role="manager")
def panel():
    """ panel/role/rolename """
    panel = dict(links=DIV(*[SPAN(A(table.replace("plugin_pyodel_", "").capitalize(),
                                  _href=URL(f="grid",
                                           args=["table", table])),
                                           _class="plugin_pyodel panel item") \
                                           for table in db.tables() if \
                                           (table.startswith("plugin_pyodel_") or \
                                           table.startswith("wiki_") or \
                                           (table == "auth_membership"))]))
    return dict(panel=panel)

def sandglass():
    """args <base action>/sandglass/<id>/question/<int>"""
    result = script = None
    if not "plugin_pyodel_sandglass" in session.keys():
        session.plugin_pyodel_sandglass = \
        plugin_pyodel_get_quiz(request.args[1])
        
    data = session.plugin_pyodel_sandglass

    if request.args(3) is not None:
        data["current"] = int(request.args[3])
    elif data["current"] is None:
        data["current"] = data["order"][0]

    question = data["questions"][data["current"]]
    options = []
    marked = list(question["marked"])

    for a in question["order"]:
        answer = question["answers"][a]
        options.append((a, answer["answer"]))

    multiple = question["multiple"]

    if len(marked) > 0:
        if multiple:
            default = marked
        else:
            default = marked[0]
    else:
        default = None

    if multiple:
        field = Field("answer", "list:integer",
                    requires=IS_IN_SET(options,
                                        multiple=True),
                    default=default)
    else:
        field = Field("answer", "integer",
                    requires=IS_IN_SET(options),
                    default=default,
                    widget=SQLFORM.widgets.radio.widget)

    form = SQLFORM.factory(field,
                           Field("done", "boolean",
                           default=False, label=T("I'm done!")),
                           _id="plugin_pyodel_sandglass_form")

    sandglass = db.plugin_pyodel_sandglass[data["sandglass"]]

    if form.process(formname="plugin_pyodel_sandglass_form").accepted:
        question = data["questions"][data["current"]]
        question["marked"] = set()
        if question["multiple"]:
            [question["marked"].add(int(value)) for \
            value in form.vars.answer]
        else:
            question["marked"].add(int(form.vars.answer))
        try:
            next = data["order"][\
            data["order"].index(data["current"]) + 1]
        except (IndexError, ValueError):
            next = data["order"][0]
            
        data["current"] = next
        
        try:
            timedout = sandglass.ends < request.now
        except TypeError:
            timedout = False

        if form.vars.done or timedout:
            plugin_pyodel_set_quiz(data)
            result = T("End of the quiz. Thank you")
        else:
            url = URL(c="plugin_pyodel", f="sandglass.load",
                      args=["sandglass", request.args[1],
                            "question", next])
            script = SCRIPT("""
            plugin_pyodel_sandglass_form_load('%(url)s');
            """ % dict(url=url))
    feedback = False
    try:
        timedout = sandglass.ends < request.now
    except TypeError:
        timedout = False
    if sandglass.feedback or timedout:
        feedback = True
    return dict(form=form, data=data, result=result,
                question=question, script=script,
                feedback=feedback, sandglass=sandglass)


def gradebook():
    import simplejson
    message = None
    mode = request.args(3)
    spreadsheet = None
    try:
        student_id = int(request.args[1])
    except (TypeError, ValueError), e:
        raise HTTP(500,
              T("The user reference is invalid or was not provided"))
    try:
        gradebook = db(db.plugin_pyodel_gradebook.student == \
                       student_id).select().first()
        gradebook_id = gradebook.id
        instances = gradebook.instances
        if instances in [None, []]:
            raise HTTP(200,
                       T("The requested gradebook has no instances."))
    except (AttributeError, KeyError), e:
        instances = [instance.id for instance in \
        db(db.plugin_pyodel_instance).select()]
        if len(instances) <= 0:
            instances = None
        gradebook_id = \
        db.plugin_pyodel_gradebook.insert(student=auth.user_id,
                                          instances=instances)
        gradebook = db.plugin_pyodel_gradebook[gradebook_id]
        message = T("New gradebook created")

    # groupby=db.plugin_pyodel_course.name,
    # orderby=db.plugin_pyodel_grade.instance
    grades = db((db.plugin_pyodel_course.id == \
                 db.plugin_pyodel_grade.course) & \
                (db.plugin_pyodel_grade.gradebook == gradebook_id) \
               ).select(orderby=db.plugin_pyodel_course.name)

    # TODO:
    # check permissions show/edit record

    # count courses
    courses = set([row.plugin_pyodel_grade.course for row in grades])
    courses.add(None)
    courses = list(courses)

    # Make an ordered sequence of instances for this gradebook
    if instances is None:
        instances = []

    unsorted_instances = [(db.plugin_pyodel_instance[instance].ordered,
                           instance,
                           db.plugin_pyodel_instance[instance]) \
                           for instance in instances]
    sorted_instances = sorted(unsorted_instances)
    sorted_instances.insert(0, (None, None, None))
    sorted_instances_as_list = [si[1] for si in sorted_instances]

    readonly = mode == "edit" or True
    import gluon.contrib.spreadsheet
    sheet = gluon.contrib.spreadsheet.Sheet(len(courses),
                                            len(sorted_instances),
                                            readonly=readonly)
    # header
    cell_r = "even"
    cell_c = None
    for x in range(len(sorted_instances)):
        cell_c = even_or_odd(x)
        if x == 0:
            sheet.cell("r0c0", value=T("Course name"),
            readonly=readonly)
        else:
            instance = sorted_instances[x][2]
            sheet.cell("r0c%s" % x,
                       value= "%(name)s (%(abbreviation)s)" % \
                           dict(name=instance.name,
                                abbreviation=instance.abbreviation),
                                readonly=readonly)

    # client-side grade data
    gradebook_data = dict()

    for x, row in enumerate(grades):
        score = row.plugin_pyodel_grade.score
        course = int(row.plugin_pyodel_course.id)
        instance = int(row.plugin_pyodel_grade.instance.id)
        # TODO: static data or formula (compute
        # values with other instances)
        name = row.plugin_pyodel_course.name
        try:
            course_position = courses.index(course)
            instance_position = sorted_instances_as_list.index(instance)
        except (ValueError, IndexError):
            # TODO: remove unresolved grade/instance/course references
            continue
        cell_c = even_or_odd(instance_position)
        cell_r = even_or_odd(course_position)
        # set or overwrite the course name value
        sheet.cell("r%sc0" % course_position,
                   value=name, readonly=True)
        readonly = (mode == "view") or \
                   (not (auth.has_membership(role="manager") or \
                         auth.has_membership(role="evaluator")))
        # set the sheet score for this course instance
        cell = "r%sc%s" % (course_position, instance_position)
        sheet.cell(cell, value=score, readonly=readonly)
        grade_data = row.plugin_pyodel_grade.as_dict()
        # json dumps error with datetime objects
        grade_data["signed"] = str(grade_data["signed"])
        gradebook_data[cell] = \
            dict(score=score,
                 formula=row.plugin_pyodel_grade.formula,
                 grade=row.plugin_pyodel_grade.id,
                 abbreviation=\
                 row.plugin_pyodel_grade.instance.abbreviation,
                 course=row.plugin_pyodel_course.id,
                 grade_data=grade_data)

    processed_data = gradebook_spreadsheet_process(gradebook_data)
    data = simplejson.dumps(processed_data)

    if mode == "view":
        form = crud.read(db.plugin_pyodel_gradebook, gradebook_id)
    elif mode == "edit" and auth.has_membership(role="manager"):
        form = crud.update(db.plugin_pyodel_gradebook, gradebook_id)
    else:
        raise HTTP(500, T("Invalid mode (or none) specified"))

    return dict(grades=grades, gradebook=gradebook,
                message=message, mode=mode, sheet=sheet,
                data=data)

@auth.requires(auth.has_membership(role="manager") or \
               auth.has_membership(role="evaluator"))
def grade():
    mode = request.args(3)
    db.plugin_pyodel_grade.id.readable = False
    try:
        gradebook_id = int(request.args[1])
    except (IndexError, ValueError, KeyError):
        if mode == "create":
            gradebook_id = None
        else:
            raise IndexError("No grade id specified")
    if mode == "create":
        db.plugin_pyodel_grade.gradebook.default = gradebook_id
        form = crud.create(db.plugin_pyodel_grade,
                           formname="plugin_pyodel_create_gradebook_form")
    elif mode == "update":
        grade_id = db.plugin_pyodel_grade[int(request.args[5])]
        form = crud.update(db.plugin_pyodel_grade, grade_id,
                           formname="plugin_pyodel_update_gradebook_form")
    elif mode == "read":
        grade_id = db.plugin_pyodel_grade[int(request.args[5])]
        form = crud.read(db.plugin_pyodel_grade, grade_id)
    else:
        raise HTTP(500, T("%s is not implemented") % mode)
    return dict(form=form)

def wiki():
    return auth.wiki()

def gradebook_spreadsheet_update():
    """ todo: name-value replacement loop"""
    import simplejson
    data = simplejson.loads(request.vars.data)
    processed_data = gradebook_spreadsheet_process(data)
    result = simplejson.dumps(dict(message="ok", newdata=processed_data))
    return result

def gradebook_spreadsheet_process(data):
    instances = set([v["abbreviation"] for v in data.values()])
    def replace_abbr(course, abbreviation, formula):
        # loop for retrieving recursively all values
        for instance in instances:
            if instance in formula:
                for k, v in data.iteritems():
                    if (v["course"] == course) and \
                       (v["abbreviation"] == instance):
                        if not v["formula"] in ["", None]:
                            if abbreviation in v["formula"]:
                                raise HTTP(200, " ".join(\
                                    ["Circular reference for", k, 
                                     "and", abbreviation]))
                            subformula = "(%s)" % v["formula"]
                            formula = replace_abbr(course,
                                                   abbreviation,
                                                    subformula)
                        else:
                            formula = "(%s)" % \
                            formula.replace(instance,
                                            str(v["score"]))
        return formula

    cells = [k for k in data.keys() \
             if data[k]["formula"] in ["", None]] + \
            [k for k in data.keys() \
            if not (data[k]["formula"] in ["", None])]

    for k in cells:
        v = data[k]
        if not v["formula"] in ["", None]:
            raw_formula = replace_abbr(v["course"],
                                       v["abbreviation"],
                                       v["formula"])
            try:
                data[k]["score"] = eval(raw_formula)
            except TypeError, e:
                data[k]["score"] = "<error!: %s>" % str(e)

        score = data[k]["score"]
        grade_score = data[k]["grade_data"]["score"]
        formula = data[k]["formula"]
        grade_formula = data[k]["grade_data"]["formula"]
        grade = data[k]["grade"]
        try:
            same_score = float(score) == float(grade_score)
        except (ValueError, TypeError):
            same_score = score == grade_score
        if (not same_score) or \
           (formula != grade_formula):
            db.plugin_pyodel_grade[grade].update_record(\
                score=score,
                formula=formula)
    return data

def admission():
    # give a student access to the site resources
    import simplejson
    course = db.plugin_pyodel_course[int(request.args[1])]
    attendance = db(db.plugin_pyodel_attendance.course == course.id)
    attendees = [attendee.student.id for attendee in \
                 attendance((db.plugin_pyodel_attendance.allowed == True) & \
                    (db.plugin_pyodel_attendance.passed != True)).select()]
    form = SQLFORM.factory(Field("students", "list:reference auth_user",
                               requires=IS_IN_DB(db, db.auth_user,
                                   "%(first_name)s %(last_name)s (%(id)s)",
                               multiple=True), default=attendees),
                           _id="plugin_pyodel_admission_form")
    if form.process(formname="plugin_pyodel_admission_form").accepted:
        if request.vars.students == None: request.vars.students = []
        for student in request.vars.students:
            vars = dict(course=course, student=student, allowed=True)
            attendee = db(db.plugin_pyodel_attendance.student == \
                          student).select().first()
            if attendee is None:
                attendee_id = db.plugin_pyodel_attendance.insert(**vars)
            else:
                attendee.update_record(**vars)
                attendee_id = attendee.id
            # Initial attendee db setup
            plugin_pyodel_attendance_setup(attendee_id)
        for attendee in attendance.select():
            if not str(attendee.student.id) in request.vars.students:
                # WARNING: all non selected attendances will be removed
                # (including those with payments recorded)
                attendee.delete_record()
        form=T("Done!")
    return dict(form=form, course=course, attendance=attendance.select())

@auth.requires(auth.has_membership(role="manager") or \
               auth.has_membership(role="evaluator"))
def bureau():
    # teacher panel
    # expose lists of courses evaluations and gradebooks
    # and teacher related stats
    workspace = DIV(_id="plugin_pyodel_desk_workspace",
                    _class="plugin_pyodel workspace")
    courses = db(db.plugin_pyodel_course).select()
    return dict(workspace=workspace, courses=courses)

def desk():
    # attendance panel
    # expose lists of courses and evaluations 
    # and student related stats
    courses = db((db.plugin_pyodel_attendance.student == auth.user_id) & \
                 (db.plugin_pyodel_attendance.course == \
                  db.plugin_pyodel_course.id) & \
                 (db.plugin_pyodel_attendance.allowed == True)).select()
    workspace = DIV(_id="plugin_pyodel_desk_workspace",
                    _class="plugin_pyodel workspace")
    """
    evaluations = {}
    for row in courses:
        course_id = row.plugin_pyodel_course.id
        attendee_id = row.plugin_pyodel_attendance.id
        evaluations[course_id] = dict(evaluations=\
          db((db.plugin_pyodel_evaluation.course == \
                                 course_id) & \
          (db.plugin_pyodel_evaluation.students.contains(\
                                 attendee_id))).select(),
          course=row.plugin_pyodel_course)
    """
    hourglasses = []
    sandglasses = []
    works = []
    for row in courses:
        attendee_id = row.plugin_pyodel_attendance.id
        evaluations=db(db.plugin_pyodel_evaluation.students.contains(\
                        attendee_id)).select()
        for evaluation in evaluations:
            sandglasses += [sandglass for sandglass in \
                            evaluation.plugin_pyodel_sandglass.select()]
            works += [work for work in evaluation.plugin_pyodel_work.select()]
            hourglasses += [hourglass for hourglass in \
                            evaluation.plugin_pyodel_hourglass.select()]
    return dict(courses=courses, workspace=workspace,
                hourglasses=hourglasses, works=works,
                sandglasses=sandglasses)

def lecture():
    # study (or edit) a lecture
    lecture = db.plugin_pyodel_lecture[request.args[1]]
    streams = [db.plugin_pyodel_stream[stream] for stream in \
               lecture.streams]
    documents = [db.wiki_page[document] for document in lecture.documents]
    stream_workspace=DIV(_id="plugin_pyodel_lecture_stream",
                         _class="plugin_pyodel workspace")
    return dict(lecture=lecture, streams=streams, documents=documents,
                stream_workspace=stream_workspace)

def course():
    # attend (or edit) a course
    course = db.plugin_pyodel_course[request.args[1]]
    attendance = db((db.plugin_pyodel_attendance.student == \
                     auth.user_id) & \
                    (db.plugin_pyodel_attendance.course == \
                     course.id)).select().first()
    lectures = db(db.plugin_pyodel_lecture.course == course.id).select()
    documents = [db.wiki_page[document] for document in course.documents]
    streams = [db.plugin_pyodel_stream[stream] for stream in \
               course.streams]
    evaluations_query = db.plugin_pyodel_evaluation.course == course.id
    evaluations_query &= \
        db.plugin_pyodel_evaluation.students.contains(attendance.id)
    evaluations = db(evaluations_query).select()

    workspace = DIV(_id="plugin_pyodel_lecture_workspace",
                    _class="plugin_pyodel workspace")
    stream_workspace = DIV(_id="plugin_pyodel_course_stream",
                           _class="plugin_pyodel workspace")
    return dict(workspace=workspace,
                course=course, lectures=lectures, documents=documents,
                streams=streams, stream_workspace=stream_workspace,
                evaluations=evaluations)

def task():
    # give a task to students
    return dict()

def work():
    # complete a course task
    db.plugin_pyodel_work.id.readable = False
    db.plugin_pyodel_work.task.writable = \
    db.plugin_pyodel_work.evaluation.writable = \
    db.plugin_pyodel_work.ends.writable = False
    form=SQLFORM(db.plugin_pyodel_work, request.args[1],
                 fields=["body", "task", "ends", "evaluation",
                         "documents"],
                 deletable=False)
    if form.process(formname="plugin_pyodel_work_form").accepted:
        form=T("Done!")
    return dict(form=form)

def stream():
    # access to media
    stream = db.plugin_pyodel_stream[request.args[1]]
    return dict(stream=stream)

def hourglass():
    # take an exam
    hourglass = db.plugin_pyodel_hourglass[request.args[1]]
    test = db.plugin_pyodel_test[hourglass.test]
    for question in test.questions:
        db.plugin_pyodel_retort.update_or_insert(hourglass=hourglass.id,
                                                 question=question)
    retorts = db(db.plugin_pyodel_retort.hourglass == \
                 hourglass.id).select()
    workspace=DIV(_id="plugin_pyodel_hourglass_workspace",
                  _class="plugin_pyodel workspace")
    return dict(workspace=workspace, hourglass=hourglass,
                retorts=retorts)

def retort():
    retort = db.plugin_pyodel_retort[request.args[1]]
    db.plugin_pyodel_retort.id.readable = False
    form = SQLFORM(db.plugin_pyodel_retort,
                   retort.id,
                   fields=["answers", "body"])
    result = None
    question = retort.question
    if form.process(formname="plugin_pyodel_retort_form").accepted:
        retorts = db(db.plugin_pyodel_retort.hourglass == \
                     retort.hourglass).select()
        form = T("Done!")
        question = None
        result = SQLTABLE(retorts,
                          columns=["plugin_pyodel_retort.question",
                                   "plugin_pyodel_retort.answers"],
                          headers={"plugin_pyodel_retort.question": \
                                       T("Question"),
                                   "plugin_pyodel_retort.answers": \
                                       T("Current answers")})
    return dict(form=form, result=result, question=question)

@auth.requires(((auth.id_group("manager") is None) and \
                 auth.is_logged_in()) or \
                auth.has_membership("manager"))
def setup():
    report = dict()

    # look for managers
    managers_group = db(db.auth_group.role == \
                        "manager").select().first()
    if managers_group is None:
        managers_group_id = \
            db.auth_group.insert(role="manager",
                                 description="Managers group")
        report["Groups"] = T("Created a new managers group")
    else:
        managers_group_id = managers_group.id
        report["Groups"] = T("No groups created")
    managers = db(db.auth_membership.group_id == \
                  managers_group_id).count()
    if managers in [0, None]:
        db.auth_membership.insert(user_id=auth.user_id,
                                  group_id=managers_group_id)
        report["Memberships"] = \
            T("Created a new managers account for this user")
    else:
        report["Memberships"] = \
            T("No memberships created")

    # if the course table is empty, create demo records
    courses = db(db.plugin_pyodel_course).count()
    if courses in [0, None]:
        import StringIO
        import plugin_pyodel.demo
        data = plugin_pyodel.demo.DATA
        sio = StringIO.StringIO()
        sio.write(data)
        sio.seek(0)
        # import os
        id_map = dict()
        for tablename in db.tables():
            id_map[tablename] = dict()
        # demo_filepath = os.path.join(request.folder,
        #                             "static", "plugin_pyodel",
        #                             "demo.csv")
        # with open(demo_filepath, "r") as demo_file:
        #    db.import_from_csv_file(demo_file, id_map=id_map)
        #    report["Records"] = T("Imported demo to db")
        db.import_from_csv_file(sio, id_map=id_map)
        sio.close()
    else:
        report["Records"] = T("Demo is already imported")

    # Add users to the demo
    report["Demo"] = dict()
    demo = db(db.plugin_pyodel_course.code==\
        "Pyodel-demo").select().first()
    if demo is not None:
        demo_attendees = [attendee.student for attendee in \
                          db(db.plugin_pyodel_attendance.course == \
                             demo.id).select()]
        report["Demo"]["Attendees"] = list()
        for user in db(db.auth_user).select():
            if not (user.id in demo_attendees):
                attendee_id = db.plugin_pyodel_attendance.insert(\
                                    student=user.id,
                                    course=demo.id,
                                    allowed=True)
                plugin_pyodel_attendance_setup(attendee_id)
                report["Demo"]["Attendees"].append(\
                    "%(first)s %(last)s" % \
                dict(first=user.first_name,
                     last=user.last_name))
    else:
        report["Demo"]["Attendees"] = T("No demo found")
    return dict(report=report)

@auth.requires_login()
def attendance():
    db.plugin_pyodel_attendance.student.writable = False
    db.plugin_pyodel_attendance.paid.readable = False
    db.plugin_pyodel_attendance.paid.writable = False
    db.plugin_pyodel_attendance.score.readable = False
    db.plugin_pyodel_attendance.score.writable = False
    db.plugin_pyodel_attendance.allowed.readable = False
    db.plugin_pyodel_attendance.allowed.writable = False
    db.plugin_pyodel_attendance.passed.readable = False
    db.plugin_pyodel_attendance.passed.writable = False

    thisyear = datetime.datetime(request.now.year, 1, 1)
    course_query = db.plugin_pyodel_course.id > 0
    course_query &= db.plugin_pyodel_course.starts >= thisyear
    for attendance in db(db.plugin_pyodel_attendance.student == \
        auth.user_id).select():
        course_query &= db.plugin_pyodel_course.id != attendance.course

    db.plugin_pyodel_attendance.course.requires = \
        IS_IN_DB(db(course_query), db.plugin_pyodel_course.id, "%(name)s")
    courses = db(course_query).select()
    form = SQLFORM(db.plugin_pyodel_attendance,
                       _id="plugin_pyodel_attendance_form")
    form.vars.student = auth.user_id
    if form.process().accepted:
        # TODO: Look for a checkout process and execute it
        # passing the new values
        if PLUGIN_PYODEL_ATTENDANCE_CHECKOUT is not None:
            course = db.plugin_pyodel_course[form.vars.course]
            PLUGIN_PYODEL_ATTENDANCE_CHECKOUT(course=course.id,
                                              attendance=form.vars.id,
                                              student=form.vars.student,
                                              code=course.code,
                                              cost=course.cost)
        form = T("New attendance created. Thanks")
    return dict(form=form, courses=courses)

@auth.requires_login()
def evaluation():
    # view or edit a student evaluation
    # presents different evaluation instances
    db.plugin_pyodel_evaluation.id.readable = False
    evaluation = db.plugin_pyodel_evaluation[request.args[1]]
    return dict(evaluation=evaluation)

