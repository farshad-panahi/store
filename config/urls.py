
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
	path("__debug__/", include("debug_toolbar.urls")),
	path("", include('store.urls')),
]
