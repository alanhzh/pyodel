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

def even_or_odd(x):
    eoo = "odd"
    is_even = int(x) % 2 == 0
    if is_even:
        eoo = "even"
    return eoo

####################################################################
######################### Plugin components ########################
####################################################################

from gluon.tools import Wiki
if request.function in ["grid", "panel"]:
    # create wiki tables
    awiki = Wiki(auth)

@auth.requires_membership(role="manager")
def grid():
    """ grid/table/tablename """
    table = request.args[1]
    return dict(grid=SQLFORM.smartgrid(db[table], args=request.args[:2]),
                back=A("Back to panel", _href=URL(f="panel")))

@auth.requires_membership(role="manager")
def panel():
    """ panel/role/rolename """
    panel = dict(links=DIV(*[SPAN(A(table.replace("plugin_pyodel_", "").capitalize(),
                                 _href=URL(f="grid",
                                           args=["table", table])), _class="plugin_pyodel panel item") \
                            for table in db.tables() if table.startswith("plugin_pyodel_")]))
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

    # TODO: different field denfinition by multiple/non-multiple value
    form = SQLFORM.factory(field,
                           Field("done", "boolean",
                           default=False, label=T("I'm done!")),
                           _id="plugin_pyodel_sandglass_form")

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
        
        if form.vars.done:
            plugin_pyodel_set_quiz(data)
            result = T("End of the quiz. Thank you")
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

    # make an ordered sequence of instances for this gradebook
    if instances is None:
        instances = []
    unsorted_instances = [(instance.ordered,
                           instance) \
                           for instance in instances]
    sorted_instances = sorted(unsorted_instances)
    sorted_instances.insert(0, (None, None))
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
            sheet.cell("r0c%s" % x, value= "%(name)s %(abbreviation)s" % dict(name=db.plugin_pyodel_instance[sorted_instances[x][1]].name, abbreviation=db.plugin_pyodel_instance[sorted_instances[x][1]].abbreviation),
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
        course_position = courses.index(course)
        instance_position = sorted_instances_as_list.index(instance)
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
        gradebook_data[cell] = \
            dict(score=score,
                 formula=row.plugin_pyodel_grade.formula,
                 grade=row.plugin_pyodel_grade.id, abbreviation=\
                 row.plugin_pyodel_grade.instance.abbreviation,
                 course=row.plugin_pyodel_course.id)

    data=simplejson.dumps(gradebook_data)

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
    gradebook_id = int(request.args[1])
    mode = request.args(3)
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
    return "ok"

def gradebook_spreadsheet_process(data):
    draft_data = data.copy()
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
                                raise HTTP(200,
                                           "".join(["Circular reference for ",
                                                    k, " and ", abbreviation]))
                            subformula = "(%s)" % v["formula"]
                            formula = replace_abbr(course, abbreviation, subformula)
                        else:
                            formula = "(%s)" % formula.replace(instance,
                                                               v["score"])
        return formula
    for k, v in draft_data.iteritems():
        if not v["formula"] in ["", None]:
            raw_formula = replace_abbr(v["course"], v["abbreviation"], v["formula"])
            data[k]["score"] = eval(raw_formula)
    return data

