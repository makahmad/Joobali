from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^listfunding', views.listFunding, name='listFunding'),
	url(r'^listprovider', views.listProvider, name='listProvider'),
	url(r'^maketransfer', views.makeTransfer, name='makeTransfer'),
	url(r'^funding', views.funding, name='funding'),
	url(r'^getiavtoken', views.getIAVToken, name='getIAVToken')
]
