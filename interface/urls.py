from django.contrib import admin
from django.urls import path
from interface import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload/', views.upload),
    path('submission/', views.submission_list),
    path('homepage/', views.homepage),
    path('submission/<int:pk>', views.submission_result),
    path('done/', views.done),
    path('alive/', views.alive),
    path('', views.login),
]
