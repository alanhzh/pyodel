# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = T("Pyodel Demo")
response.subtitle = T('customize me!')

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Alan Etkin <spametki@gmail.com>'
response.meta.description = 'e-learning tools web2py plugin'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'
response.meta.copyright = 'Copyright 2011'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('Home'), False, URL('default','index'), [])
    ]

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources
    response.menu+=[
        (SPAN('Pyodel',_style='color:yellow'),False, 'http://code.google.com/p/pyodel',
                [(T('wiki'),False, 'http://code.google.com/p/pyodel/wiki'),
                 (T('issues'),False,'http://code.google.com/p/pyodel/issues')])]
_()

