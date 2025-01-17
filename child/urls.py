from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^add', views.add_child, name='addChild'),
    url(r'^list', views.list_child, name='listChild'),
    url(r'^update', views.update_child, name='updateChild'),
    url(r'^remove', views.remove_child, name='removeChild'),
    url(r'^get', views.get_child, name='getChild'),
]
