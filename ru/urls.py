from django.urls import path

from .views import trouble_shooting_views
from .views import pinmux_views
from .views import admin_views
from .views import images_views
from .views import feedback_views

urlpatterns = [
    path('', pinmux_views.index, name='index'),
    path('pinmux/get', pinmux_views.get),
    path('pinmux/save', pinmux_views.save),
    path('admin/register', admin_views.register),
    path('admin/login', admin_views.login),
    path('admin/get', admin_views.get),
    path('trouble_shooting/get', trouble_shooting_views.get),
    path('trouble_shooting/save', trouble_shooting_views.save),
    path('images/upload', images_views.upload),
    path('images/get', images_views.get),
    path('feedback/save', feedback_views.save),
    path('feedback/get', feedback_views.get),
]
