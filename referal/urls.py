from django.conf.urls import url

from referal import views

urlpatterns = [
	url(r'^$', views.referalForm),
]
