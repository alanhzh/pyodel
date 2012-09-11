# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

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
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

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

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

import random

pyodel_images = [
"https://lh5.googleusercontent.com/-69BKZfBq9Ig/UEvBb6J6cZI/AAAAAAAAApM/UbUmSq03EBg/s288/yodel-student.png",
"https://lh5.googleusercontent.com/-iKWV9_bApME/UEvBa-X-RJI/AAAAAAAAApE/cYVCOGP8JpI/s288/yodel-student-2.png",
"https://lh3.googleusercontent.com/-iBEyUbydXY0/UEvBaKrjU7I/AAAAAAAAAo8/cDtgS53MHVc/s288/yodel-professor.png",
"https://lh3.googleusercontent.com/-fo9gVk8J0yE/UEvBZJynQ3I/AAAAAAAAAo0/qnubQrbmzMY/s288/yodel-professor-2.png",
"https://lh5.googleusercontent.com/-KkhXAHF5ELM/UEvBZGHFlwI/AAAAAAAAAos/MOMKxCLAi1k/s288/yodel-interview.png",
"https://lh3.googleusercontent.com/-IZAspMKuXi0/UEvBYDxf4VI/AAAAAAAAAok/PhN4PcmaT-s/s288/yodel-class.png"]
pyodel_image = random.choice(pyodel_images)

db.define_table("applicant",
                Field("say", label=T("Say..."),
                      comment=T("Why you want to be a manager? (please do not put something reasonable here)"),
                      requires=IS_NOT_EMPTY()),
                Field("user", "reference auth_user",
                      default=auth.user_id, writable=False),
                Field("accepted", "boolean", default=False,
                      readable=False, writable=False),
                Field("notified", "boolean", default=False,
                      writable=False, readable=False))

