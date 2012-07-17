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

# TODO: move the model fields config.
# to the model
plugin_pyodel_configure_model()

####################################################################
############### Plugin controller local functions ##################
####################################################################

def even_or_odd(x):
    eoo = "odd"
    is_even = int(x) % 2 == 0
    if is_even:
        eoo = "even"
    return eoo

####################################################################
######################### Plugin components ########################
####################################################################


def quiz():
    data = plugin_pyodel_get_quiz(db(db.plugin_pyodel_sandglass).select().first().id)
    return dict(data=data)


def sandglass():
    """args <base action>/sandglass/<id>/question/<int>"""
    result = script = None
    if not "plugin_pyodel_sandglass" in session.keys():
        session.plugin_pyodel_sandglass = \
        plugin_pyodel_get_quiz(request.args[1])
        
    data = session.plugin_pyodel_sandglass

    if request.args(3) is not None:
        data["current"] = int(request.args(3))
    elif data["current"] is None:
        data["current"] = data["order"][0]

    print "current is", data["current"]

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

    # TODO: different field denfinition by multiple/non-multiple value
    form = SQLFORM.factory(field,
                           Field("done", "boolean",
                           default=False, label=T("I'm done!")),
                           _id="plugin_pyodel_sandglass_form")

    if form.process(formname="plugin_pyodel_sandglass_form").accepted:
        print "processing question number", data["current"]
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
        
        if form.vars.done:
            plugin_pyodel_set_quiz(data)
            result = db.plugin_pyodel_sandglass[data["sandglass"]]
        else:
            url = URL(c="plugin_pyodel", f="sandglass.load",
                      args=["sandglass", request.args[1],
                            "question", next])
            script = SCRIPT("""
            plugin_pyodel_sandglass_form_load('%(url)s');
            """ % dict(url=url))
    return dict(form=form, data=data, result=result,
                question=question, script=script)


def gradebook():
    message = None
    mode = request.args(3)
    spreadsheet = None
    try:
        student_id = int(request.args[1])
    except (TypeError, ValueError), e:
        raise HTTP(500, \
T("The user reference is invalid or was not provided"))
    try:
        gradebook = db(db.plugin_pyodel_gradebook.student == \
                       student_id).select().first()
        gradebook_id = gradebook.id
        instances = gradebook.instances
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

    grades = db((db.plugin_pyodel_grade.course == \
                     db.plugin_pyodel_course.id) & \
                     (db.plugin_pyodel_grade.gradebook == \
                gradebook_id)).select(groupby=\
                db.plugin_pyodel_course.name,
                orderby=db.plugin_pyodel_grade.instance)

    # TODO:
    # check permissions show/edit record

    # count courses
    courses = set([row.plugin_pyodel_grade.course for row in grades])
    courses.add(None)
    courses = list(courses)

    # make an ordered sequence of instances for this gradebook
    if instances is None:
        instances = []
    unsorted_instances = [(instance.ordered,
                           instance) \
                           for instance in instances]
    sorted_instances = sorted(unsorted_instances)
    sorted_instances.insert(0, (None, None))
    sorted_instances_as_list = [si[1] for si in sorted_instances]

    readonly = "edit" in request.args(3) or True

    import gluon.contrib.spreadsheet
    sheet = gluon.contrib.spreadsheet.Sheet(len(courses),
                                            len(sorted_instances),
                                            readonly=readonly)
    # _class="plugin_pyodel_sheet"

    # header
    cell_r = "even"
    cell_c = None
    for x in range(len(sorted_instances)):
        cell_c = even_or_odd(x)
        if x == 0:
            sheet.cell("r0c0", value=T("Course name"),
            readonly=readonly)
            # _class="plugin_pyodel-sheet-cell-row-%s-col-%s-header" % \
            # (cell_r, cell_c)
        else:
            sheet.cell("r0c%s" % x, value= \
            db.plugin_pyodel_instance[sorted_instances[x][1]].name,
            readonly=readonly)
            # _class="plugin_pyodel-sheet-cell-row-%s-col-%s-header" % \
            # (cell_r, cell_c)

    # INCOMPLETE: add course rows/cells with score data
    for x, row in enumerate(grades):
        score = row.plugin_pyodel_grade.score
        course = int(row.plugin_pyodel_course.id)
        instance = int(row.plugin_pyodel_grade.instance.id)
        # TODO: static data or formula (compute
        # values with other instances)
        name = row.plugin_pyodel_course.name
        course_position = courses.index(course)
        instance_position = sorted_instances_as_list.index(instance)
        cell_c = even_or_odd(instance_position)
        cell_r = even_or_odd(course_position)
        # set or overwrite the course name value
        sheet.cell("r%sc0" % course_position, value=name)
        # _class="plugin_pyodel-sheet-cell-row-%s-col-%s-course" % \
        # (cell_r, cell_c)
        # set the sheet score for this course instance
        sheet.cell("r%sc%s" % (course_position, instance_position),
                   value=score)
        # _class="plugin_pyodel-sheet-cell-row-%s-col-%s-value" % \
        # (cell_r, cell_c)

    if mode == "view":
        form = crud.read(db.plugin_pyodel_gradebook, gradebook_id)
    elif mode == "edit":
        form = crud.update(db.plugin_pyodel_gradebook, gradebook_id)
    else:
        raise HTTP(500, T("Invalid mode (or none) specified"))

    # tag = TAG(sheet.xml())

    return dict(grades=grades, gradebook=gradebook,
                message=message, mode=mode, sheet=sheet)


def grade():
    gradebook_id = int(request.args(1))
    mode = request.args(3)
    if mode == "create":
        db.plugin_pyodel_grade.gradebook.default = gradebook_id
        form = crud.create(db.plugin_pyodel_grade, \
                 formname="plugin_pyodel_create_gradebook_form")
    elif mode == "update":
        grade_id = db.plugin_pyodel_grade[int(request.args(5))]
        form = crud.update(db.plugin_pyodel_grade, grade_id, \
                 formname="plugin_pyodel_update_gradebook_form")
    else:
        raise HTTP(500, T("%s is not implemented") % mode)
    return dict(form=form)

