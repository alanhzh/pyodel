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
    actions = UL(LI(A(T("Student's desk"),
                      _href=URL(c="default",
                                f="desk.html"))),
                 LI(A(T("Teacher's bureau"),
                      _href=URL(c="default",
                                f="bureau.html"))),
                 LI(A(T("Manager panel"),
                      _href=URL(c="plugin_pyodel",
                                f="panel.html"))),
                 LI(A(T("Wiki"),
                      _href=URL(c="plugin_pyodel",
                                f="wiki.html"))),
                 LI(A(T("Setup"),
                      _href=URL(c="plugin_pyodel",
                                f="setup.html"))),
                 LI(A(T("Submit a quiz proposal"),
                      _href=URL(c="default",
                                f="quiz.html"))))
    response.flash = T("Welcome to Pyodel!")
    return dict(message=T('Explore the plugin features'), actions=actions)

    
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
