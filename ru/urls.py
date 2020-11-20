from django.urls import path

from .views import trouble_shooting_views
from .views import pinmux_views
from .views import admin_views

urlpatterns = [
    path('', pinmux_views.index, name='index'),
    path('pinmux/get', pinmux_views.get),
    path('pinmux/save', pinmux_views.save),
    path('admin/register', admin_views.register),
    path('trouble_shooting/get', trouble_shooting_views.get),
    path('trouble_shooting/save', trouble_shooting_views.save),
]
