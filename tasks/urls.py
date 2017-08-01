from django.conf.urls import url

from tasks import views

urlpatterns = [
	url(r'^datacleaning/', views.data_cleaning, name='dataCleaning'),
	url(r'^invoicecalc/', views.invoice_calculation, name='invoiceCalculation'),
	url(r'^invoicenoti/', views.invoice_notification, name='invoiceNotification'),
	url(r'^autopay/', views.autopay, name='autopay'),
	url(r'^dwollawebhook/', views.dwolla_webhook, name='dwollaWebhook'),
	url(r'^dwolla_webhook_setup/', views.dwolla_webhook_setup, name='dwollaWebhookSetup'),
	url(r'^dwolla_token_refresh/', views.dwolla_token_refresh, name='dwollaTokenRefresh'),
	url(r'^process_fee/', views.process_fee, name='processFee'),
]
