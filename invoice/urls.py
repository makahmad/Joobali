from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^listinvoices', views.listInvoices, name='listInvoices'),
	url(r'^setupautopay', views.setupAutopay, name='setupAutopay'),
	url(r'^markpaid', views.markPaid, name='markPaid'),
	url(r'^viewinvoice', views.viewInvoice, name='viewInvoice'),
	url(r'^addinvoice', views.add_invoice, name='addInvoice'),
]
