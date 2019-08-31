from django.contrib import admin
from django.urls import path
from interface import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload/', views.upload),
    path('submission/', views.submission),
    path('done/', views.done),
    path('alive/', views.alive),
    path('', views.homepage),
]
