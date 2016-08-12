import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'joobali.settings'

import sys
sys.path.append('lib')
sys.path.append('/Users/Ryan/workspace/google-cloud-sdk/platform/google_appengine/lib/django-1.5')
import django.core.handlers.wsgi

from requests_toolbelt.adapters import appengine
appengine.monkeypatch()

application = django.core.handlers.wsgi.WSGIHandler()
