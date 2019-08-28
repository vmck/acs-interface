from django.contrib import admin
from django.urls import path
from interface import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload/', views.upload),
    path('done/', views.done),
    path('', views.homepage),
]
