from django.contrib import admin
from django.urls import path, include

admin.site.site_header = 'Site header'
admin.site.index_title = 'Site title'

urlpatterns = [
	path('admin/', admin.site.urls),
	path("__debug__/", include("debug_toolbar.urls")),
	path("", include('store.urls')),
]
