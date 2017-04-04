from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^listinvoices', views.listInvoices, name='listInvoices'),
	url(r'^addpayment', views.add_payment, name='addPayment')
]
