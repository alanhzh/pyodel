# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simple replace the two lines below with:
    return auth.wiki()
    """
    message = T('Explore the plugin features')
    applicant = db((db.applicant.user==auth.user_id) & \
                   (db.applicant.accepted==True) & \
                   (db.applicant.notified==False)).select().first()
    if applicant is not None:
        message = T("Congratulations. You now belong to the managers group")
        applicant.update_record(notified=True)
    actions = UL(LI(A(T("Student's desk"),
                      _href=URL(c="default",
                                f="desk.html"),
                      _onmouseover="jQuery('#plugin_pyodel_demo_aid').html('%s');" % \
                          T("For any registered user"))),
                 LI(A(T("Teacher's bureau"),
                      _href=URL(c="default",
                                f="bureau.html"),
                      _onmouseover="jQuery('#plugin_pyodel_demo_aid').html('%s');" % \
                          T("Only those who teach shall pass"))),
                 LI(A(T("Manager panel"),
                      _href=URL(c="plugin_pyodel",
                                f="panel.html"),
                      _onmouseover="jQuery('#plugin_pyodel_demo_aid').html('%s');" % \
                          T("If you ever managed something, you know what this is about"))),
                 LI(A(T("Wiki"),
                      _href=URL(c="plugin_pyodel",
                                f="wiki.html"),
                                _onmouseover="jQuery('#plugin_pyodel_demo_aid').html('%s');" % \
                                    T("Wikis are the new amazing web2py built-in docs system"))),
                 LI(A(T("Setup"),
                      _href=URL(c="plugin_pyodel",
                                f="setup.html"),
                                _onmouseover="jQuery('#plugin_pyodel_demo_aid').html('%s');" % \
                                    T("Click here if you really know what you are doing"))),
                 LI(A(T("Submit a quiz proposal"),
                      _href=URL(c="default",
                                f="quiz.html"),
                                _onmouseover="jQuery('#plugin_pyodel_demo_aid').html('%s');" % \
                                    T("Please, please, do! It is as easy as yodeling without diploma"))),
                 LI(A(T("I want to be a teacher or manager or whatever"),
                      _href=URL(c="default",
                                f="newmanager.html"),
                                _onmouseover="jQuery('#plugin_pyodel_demo_aid').html('%s');" % \
                                    T("Perhaps just being a student is not enough for you"))))
    if auth.has_membership(role="manager"):
        actions.append(LI(A(T("Add new managers"),
                      _href=URL(c="default",
                                f="addmanagers.html"),
                                _onmouseover="jQuery('#plugin_pyodel_demo_aid').html('%s');" % \
                                    T("You never know when you need them"))))
    response.flash = T("Welcome to Pyodel!")
    return dict(message=message, actions=actions,
                aid=H3(T("Welcome!"), _id="plugin_pyodel_demo_aid"))

@auth.requires_login()
def newmanager():
    form = crud.create(db.applicant)
    if form.process().accepted:
        response.flash = T("Your application has been recorded. Thanks")
    return dict(form=form)

@auth.requires_membership(role="manager")
def addmanagers():
    memberships = list()
    applicants = db(db.applicant.accepted == False).select()
    applicants_set = dict()
    for applicant in applicants:
        applicants_set[applicant.id] = "%(first)s %(last)s" % \
                                           dict(first=applicant.user.first_name,
                                                last=applicant.user.last_name)
    form = SQLFORM.factory(Field("applicants", "list:integer",
                           requires=IS_IN_SET(applicants_set, multiple=True)))
    if form.process().accepted:
        for applicant_id in form.vars.applicants:
            applicant = db.applicant[applicant_id]
            group = db(db.auth_group.role=="manager").select().first()
            db.auth_membership.insert(group_id=group.id,
                                      user_id=applicant.user)
            applicant.update_record(accepted=True)
            memberships.append(applicants_set[int(applicant_id)])
        form = None
    return dict(form=form, memberships=memberships, applicants=applicants)

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

@auth.requires_login()
def desk():
    desk = LOAD(c="plugin_pyodel", f="desk.load", ajax=True)
    return dict(desk=desk)

@auth.requires_login()
def bureau():
    bureau = LOAD(c="plugin_pyodel", f="bureau.load", ajax=True)
    return dict(bureau=bureau)

@auth.requires_login()
def quiz():
    db.plugin_pyodel_quiz.body.comment = MARKMIN("""
### Quiz syntax:

- ``Quiz instructions are interpreted by line (line-breaks terminate them).``:gray
- ``Note that answers will appear in the given order unless sh: (for shuffle)``:gray
- ``is added to each question group``:gray:

.

- q: The actual question goes here. Ok?
- c: C stands for correct answer (I guess)
- i: I'm afraid this is an incorrect answer
- i: This too is wrong
- i: Another one
- s: 1.232 # score for this question (not mandatory)
- m: # this is for allowing multiple answers
- sh: # add this so the answers are mixed

.

- q: Here's another question. ¿What about it?
- c: ...
- i: ...

.
""")
    db.plugin_pyodel_quiz.name.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, db.plugin_pyodel_quiz.name)]
    db.plugin_pyodel_quiz.body.requires = IS_NOT_EMPTY()
    form = crud.create(db.plugin_pyodel_quiz)
    if form.process().accepted:
        response.flash = T("Thank you")
    return dict(form=form)

"""
@auth.requires_membership(role="manager")
def demo():
    import StringIO
    myfile = StringIO.StringIO()
    db.export_to_csv_file(myfile)
    myfile.seek(0)
    return response.stream(myfile, attachment=True)
"""

