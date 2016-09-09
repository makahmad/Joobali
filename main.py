import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'joobali.settings'

import sys
sys.path.append('lib')
import django.core.handlers.wsgi

from requests_toolbelt.adapters import appengine
appengine.monkeypatch()

application = django.core.handlers.wsgi.WSGIHandler()
