from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
	url(r'^$', 'core.views.home', name='home'),	
	url(r'^contact$', 'core.views.contact', name='contact'),
	url(r'^about$', 'core.views.about', name='about'),	
	url(r'^statistics$', 'core.views.display_chart', name='display_chart'),
	url(r'^import_data$', 'core.views.import_data', name='import_data'),
	url(r'^download_(?P<output_type>[^/]+)$', 'core.views.download', name='download'),	
	url(r'^check$', 'core.views.check', name='check'),	
	url(r'^view_(?P<view_type>[^/]+)', 'core.views.view', name='view'),	
	url(r'^galaxy_(?P<obj_id>[^/]+)', 'core.views.display_galaxy', name='display_galaxy'),	
	url(r'^pair_(?P<id>[^/]+)', 'core.views.display_pair', name='display_pair'),	
	url(r'^admin/', include(admin.site.urls)),
)
