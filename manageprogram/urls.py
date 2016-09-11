from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^listprograms', views.listPrograms, name='listPrograms'),
]
