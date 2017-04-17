from django.conf.urls import url

from helpcenter import views

urlpatterns = [
	url(r'^sendcomments', views.sendComments, name='sendComments')
]
