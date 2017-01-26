from django.conf.urls import include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    url(r'^home/', include('home.urls')),
    url(r'^manageprogram/', include('manageprogram.urls')),
    url(r'^funding/', include('funding.urls')),
    url(r'^$', include('login.urls')),
    url(r'^login/', include('login.urls')),
    url(r'^profile/', include('profile.urls')),
    url(r'^invoice/', include('invoice.urls')),
    url(r'^referal/', include('referal.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^enrollment/', include('enrollment.urls')),
    url(r'^parent/', include('parent.urls')),
    url(r'^child/', include('child.urls')),
    url(r'^tasks/', include('tasks.urls'))
    # Examples:
    # url(r'^$', 'joobali.views.home', name='home'),
    # url(r'^joobali/', include('joobali.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
]
