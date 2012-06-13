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
# plugin_pyodel components                                         #
####################################################################

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

    # header
    for x in range(len(sorted_instances)):
        if x == 0:
            sheet.cell("r0c0", value=T("Course name"),
            readonly=readonly)
        else:
            sheet.cell("r0c%s" % x, value= \
            db.plugin_pyodel_instance[sorted_instances[x][1]].name,
            readonly=readonly)

    # INCOMPLETE: add course rows/cells with score data
    for row in grades:
        score = row.plugin_pyodel_grade.score
        course = int(row.plugin_pyodel_course.id)
        instance = int(row.plugin_pyodel_grade.instance.id)
        # TODO: static data or formula (compute
        # values with other instances)
        name = row.plugin_pyodel_course.name
        course_position = courses.index(course)
        instance_position = sorted_instances_as_list.index(instance)
        # set or overwrite the course name value
        sheet.cell("r%sc0" % course_position, value=name)
        # set the sheet score for this course instance
        sheet.cell("r%sc%s" % (course_position, instance_position),
                   value=score)

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
        form = crud.create(db.plugin_pyodel_grade)
    elif mode == "update":
        grade_id = db.plugin_pyodel_grade[int(request.args(5))]
        form = crud.update(db.plugin_pyodel_grade, grade_id)
    else:
        raise HTTP(500, T("%s is not implemented") % mode)
    return dict(form=form)