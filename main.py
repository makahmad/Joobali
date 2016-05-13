import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'joobali.settings'

import sys
sys.path.append('lib')

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
