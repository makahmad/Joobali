from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^listfunding', views.listFunding, name='listFunding'),
	url(r'^listprovider', views.listProvider, name='listProvider'),
	url(r'^maketransfer', views.makeTransfer, name='makeTransfer'),
	url(r'^removefunding', views.removeFunding, name='removeFunding'),
	url(r'^getiavtoken', views.getIAVToken, name='getIAVToken'),
	url(r'^updategeneralbilling', views.updateGeneralBilling, name='updateGeneralBilling'),
	url(r'^getgeneralbilling', views.getGeneralBilling, name='getGeneralBilling')
]
