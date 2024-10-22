from django.conf.urls import include, url
from home import views as homeviews
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    url(r'^home/', include('home.urls')),
    url(r'^manageprogram/', include('manageprogram.urls')),
    url(r'^funding/', include('funding.urls')),
    url(r'^$', include('home.urls')),
    url(r'^login/', include('login.urls')),
    url(r'^payments/', include('payments.urls')),
    url(r'^profile/', include('profile.urls')),
    url(r'^invoice/', include('invoice.urls')),
    url(r'^referral/', include('referral.urls')),
    url(r'^enrollment/', include('enrollment.urls')),
    url(r'^parent/', include('parent.urls')),
    url(r'^child/', include('child.urls')),
    url(r'^tasks/', include('tasks.urls')),
    url(r'^verification/', include('verification.urls')),
    url(r'^team/', homeviews.team, name='team'),
    url(r'^match/', homeviews.match, name='match')
    # Examples:
    # url(r'^$', 'joobali.views.home', name='home'),
    # url(r'^joobali/', include('joobali.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
]
