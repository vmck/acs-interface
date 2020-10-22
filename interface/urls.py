from django.contrib import admin
from django.urls import path, include, re_path
from interface import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "assignment/<course_pk>/<assignment_pk>/upload/",
        views.upload,
        name="upload",
    ),
    path("submission/", views.submission_list, name="submission_list"),
    path("homepage/", views.homepage, name="homepage"),
    path(
        "submission/<int:pk>/",
        views.submission_result,
        name="submission_result",
    ),
    path("submission/<int:pk>/done", views.done),
    path("submission/<int:pk>/review", views.review),
    path("submission/<int:pk>/download", views.download),
    path("submission/<int:pk>/rerun", views.rerun_submission),
    path("submission/<int:pk>/recompute", views.recompute_score),
    path("alive/", views.alive),
    path("logout/", views.logout_view, name="logout"),
    path("", views.login_view, name="login"),
    path(
        "assignment/<course_pk>/<assignment_pk>",
        views.users_list,
        name="subs_for_assignment",
    ),
    path(
        "assignment/<course_pk>/<assignment_pk>/reveal",
        views.reveal,
        name="reveal",
    ),
    path(
        "assignment/<course_pk>/<assignment_pk>/user/<username>",
        views.subs_for_user,
        name="subs_for_user",
    ),
    path("mysubmissions/<username>", views.user_page, name="user_page"),
    path(
        "submission/<int:pk>/<path:filename>/",
        views.code_view,
        name="code_view",
    ),
] + [re_path(r'^silk/', include('silk.urls', namespace='silk'))]
