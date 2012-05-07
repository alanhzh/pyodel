# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

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

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite')
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db = db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db, hmac_key=Auth.get_or_create_key())
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables()

## configure email
mail=auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth,filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

""" some administrative tasks required:
A group of managers
A group of evaluators

This can be accomplished with an initial setup action

Managers will create courses and related stuff, assign them evaluators.
They will control evaluators rights.
Lastly, they will manage student subscriptions to courses
(attendance admissions)

Evaluators can assign and edit an attendant's evaluation.
"""

# By now, just update or insert the groups as needed
db.auth_group.update_or_insert(role="manager",
description="Absolute CRUD rights")
db.auth_group.update_or_insert(role="evaluator",
description="Can evaluate exams")
db.auth_group.update_or_insert(role="editor",
description="Can edit documents")

markmin_comment=T("Use MARKMIN or plain text")

db.define_table("stream",
                Field("live", "boolean", default=False),
                Field("name"),
                Field("body", "text", comment=markmin_comment),
                # embedded html code
                Field("html", "text",
                comment=T("The html code for embedding the video")),
                Field("starts", "datetime"),
                Field("ends", "datetime"),
                Field("tags", "list:string"),
                format="%(name)s"
                )

# the whole course
db.define_table("course",
                Field("active", "boolean", default=False),
                Field("template", "boolean", default=False),
                Field("code"),
                Field("name"),
                Field("streams", "list:reference stream"),
                Field("body", "text", comment=markmin_comment), # MARKMIN
                Field("by", "list:reference auth_user"),
                Field("starts", "datetime"),
                Field("documents", "list:reference plugin_wiki_page"), # STATIC PAGES
                Field("ends", "datetime"),
                Field("tags", "list:string"),
                Field("cost", "double", default=0.0),
                format="%(name)s")

# one session
db.define_table("lecture",
                Field("template", "boolean", default=False),
                Field("chapter", "integer"),
                Field("name"),
                Field("course", "reference course"),
                Field("streams", "list:reference stream"),
                Field("body", "text", comment=markmin_comment), # MARKMIN
                Field("by", "list:reference auth_user"),
                Field("documents", "list:reference plugin_wiki_page"),
                Field("tags", "list:string"),
                format="%(name)s")

db.define_table("attendance",
                Field("student", "reference auth_user",
                default=auth.user_id),
                Field("course", "reference course"),
                Field("paid", "double", default=0.0),
                Field("allowed", "boolean", default=False),
                Field("passed", default=False),
                Field("score", "double", default=0.0),
                format="%(student)s"
                )

db.define_table("task",
                Field("template", "boolean", default=False),
                Field("name"),
                Field("body", "text", comment=markmin_comment), # MARKMIN
                Field("documents",
                "list:reference plugin_wiki_page"),
                Field("tags", "list:string"),
                Field("points", "double", default=0.0),
                format="%(name)s")

db.define_table("answer",
                Field("body", "text", comment=markmin_comment), # MARKMIN
                Field("tags", "list:string"),
                format="%(body)s"
                )

# Question can be multiple choice or not, or even an exercise,
# in which case it will probably not be an actual question
db.define_table("question",
                Field("body", "text", comment=markmin_comment), # MARKMIN
                Field("tags", "list:string"),
                Field("points", "double", default=0.0),
                Field("answers", "list:reference answer"),
                Field("correct", "list:reference answer",
                readable=False),
                Field("shuffle", "boolean", default=False),
                format="%(body)s"
                )

db.define_table("quiz",
                Field("template", "boolean", default=False),
                Field("duration", "time"),
                Field("questions", "list:reference question"),
                Field("name"),
                Field("body", "text", comment=markmin_comment), # MARKMIN
                Field("tags", "list:string"),
                Field("shuffle", "boolean", default=False),
                format="%(name)s"
                )

db.define_table("evaluation",
                Field("template", "boolean", default=False),
                Field("name"),
                Field("code"), # a letter or other identifier
                Field("description", "text", comment=markmin_comment), # MARKMIN
                Field("course", "reference course"),
                Field("lectures", "list:reference lecture"),
                Field("starts", "datetime"),
                Field("ends", "datetime"),
                Field("students", "list:reference attendance"),
                Field("evaluators", "list:reference auth_user"),
                Field("quizes", "list:reference quiz"),
                Field("score", "double", default=0.0),
                Field("tags", "list:string"),
                Field("tasks", "list:reference task"),
                format="%(name)s")

# Student's task work
db.define_table("work",
                Field("body", "text", comment=markmin_comment), # MARKMIN
                Field("task", "reference task"),
                Field("starts", "datetime"),
                Field("ends", "datetime"),                
                Field("evaluation", "reference evaluation"),
                Field("documents",
                "list:reference plugin_wiki_page"),
                Field("points", "double", default=0.0),
                Field("score", "double", default=0.0),
                format="%(task)s"
                )

# A timer for a quiz
db.define_table("hourglass",
                Field("quiz", "reference quiz"),
                Field("starts", "datetime"),
                Field("ends", "datetime"),
                Field("evaluation", "reference evaluation"),
                Field("score", "double", default=0.0),
                format="%(quiz)s")

# A student's evaluation answer (can refer to an option
# or be redacted).
db.define_table("retort",
                Field("hourglass", "reference hourglass"),
                Field("question", "reference question"),
                Field("answers", "list:reference answer"),
                # MARKMIN
                Field("body", "text", comment=markmin_comment),
                Field("score", "double", default=0.0),
                format="%(answers)s"
               )

###################################################################

db.course.code.requires = IS_NOT_IN_DB(db, db.course.code)

# -*- coding: utf-8 -*-

def show_markmin(value, row):
    if request.function == "select" and request.args(1) is None:
        # grids
        if value is not None:
            return value[:20]
        else:
            return value
    else:
        # forms
        return MARKMIN(value)

def show_documents(value, row):
    if value is not None:
        return OL(*[LI(A(item.title,
                         _href=URL(r=request,
                                   c="plugin_wiki",
                                   f="page",
                                   args=[item.slug,
                                   ]))) for item in value])
    else:
        return T("Empty")

# custom validators (to be declared after plugin_wiki)

db.course.documents.requires = IS_IN_DB(db, "db.plugin_wiki_page", "%(slug)s",
                                        multiple=True)
db.course.documents.represent = show_documents
db.course.body.represent = show_markmin

db.lecture.documents.requires = IS_IN_DB(db, "db.plugin_wiki_page", "%(slug)s",
                                         multiple=True)
db.lecture.documents.represent = show_documents
db.lecture.body.represent = show_markmin

db.task.documents.requires = IS_IN_DB(db, "db.plugin_wiki_page", "%(slug)s",
                                      multiple=True)
db.task.documents.represent = show_documents
db.task.body.represent = show_markmin

db.work.documents.requires = IS_IN_DB(db, "db.plugin_wiki_page", "%(slug)s",
                                      multiple=True)
db.work.documents.represent = show_documents
db.work.body.represent = show_markmin

db.stream.body.represent = show_markmin
db.answer.body.represent = show_markmin
db.question.body.represent = show_markmin
db.quiz.body.represent = show_markmin
db.retort.body.represent = show_markmin

# Throws an exception (plugin_wiki_page is not defined)
# db.plugin_wiki_page.body.comment = markmin_comment

# This code was extracted from the following site:
# http://codereview.stackexchange.com/questions/5091/
# python-function-to-convert-roman-numerals-to-integers
# -and-vice-versa
# Author: Anthony Curtis Adler

def int_to_roman (integer):
    returnstring=''
    table=[['M',1000],['CM',900],['D',500],['CD',400],['C',100],
           ['XC',90],['L',50],['XL',40],['X',10],['IX',9],
           ['V',5],['IV',4],['I',1]]

    for pair in table:
        while integer-pair[1]>=0:
            integer-=pair[1]
            returnstring+=pair[0]
    return returnstring

def rom_to_int(string):
    table=[['M',1000],['CM',900],['D',500],['CD',400],['C',100],
           ['XC',90],['L',50],['XL',40],['X',10],['IX',9],
           ['V',5],['IV',4],['I',1]]
    returnint=0
    for pair in table:
        continueyes=True
        while continueyes:
            if len(string)>=len(pair[0]):
                if string[0:len(pair[0])]==pair[0]:
                    returnint+=pair[1]
                    string=string[len(pair[0]):]
                else: continueyes=False
            else: continueyes=False
    return returnint

# from gluon.tools import PluginManager
# plugins = PluginManager()

