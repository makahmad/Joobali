from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^listprograms', views.listPrograms, name='listPrograms'),
	url(r'^addprogram', views.addProgram, name='addProgram'),
	url(r'^getprogram', views.getProgram, name='getProgram'),
	url(r'^updateprogram', views.updateProgram, name='updateProgram'),
	url(r'^deleteprogram', views.deleteProgram, name='deleteProgram'),
	url(r'^copyprogram', views.copyProgram, name='copyProgram'),
	# url(r'^addsession', views.addSession, name='addSession'),
	# url(r'^listsessions', views.listSessions, name='listSessions'),
	# url(r'^updatesession', views.updateSession, name='updateSession'),
	# url(r'^deletesession', views.deleteSession, name='deleteSession'),
	url(r'^edit', views.edit, name='edit'),
	url(r'^getdefaultlatefee', views.getDefaultLateFee, name='getDefaultLateFee'),
	url(r'^listprogrambychild', views.list_program_by_child, name='listProgramByChild'),
]
