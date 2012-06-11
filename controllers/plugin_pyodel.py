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

    # make an ordered sequence of instances for this gradebook
    if instances is None:
        instances = []
    unsorted_instances = [(instance.ordered,
                           instance) \
                           for instance in instances]
    sorted_instances = sorted(unsorted_instances)
    sorted_instances.insert(0, (None, None))

    import gluon.contrib.spreadsheet
    sheet = gluon.contrib.spreadsheet.Sheet(len(courses),
                                            len(sorted_instances))

    # header
    for x in range(len(sorted_instances)):
        if x == 0:
            sheet.cell("r0c0", value=T("Course name"), readonly=True)
        else:
            sheet.cell("r0c%s" % x, value= \
            db.plugin_pyodel_instance[sorted_instances[x][1]].name,
            readonly=True)

    # INCOMPLETE: add course rows/cells with score data

    if mode == "view":
        form = crud.read(db.plugin_pyodel_gradebook, gradebook_id)
    elif mode == "edit":
        form = crud.update(db.plugin_pyodel_gradebook, gradebook_id)
    else:
        raise HTTP(500, T("Invalid mode (or none) specified"))

    # tag = TAG(sheet.xml())

    return dict(grades=grades, gradebook=gradebook,
                message=message, mode=mode, sheet=sheet)

