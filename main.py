import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'joobali.settings'

import sys
sys.path.append('lib')
import django.core.handlers.wsgi

from requests_toolbelt.adapters import appengine
appengine.monkeypatch()

from django.core.wsgi import get_wsgi_application
# application = django.core.handlers.wsgi.WSGIHandler()
application = get_wsgi_application()

