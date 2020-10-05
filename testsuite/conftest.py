import pytest
import threading
from datetime import datetime, timezone
from http.server import HTTPServer, SimpleHTTPRequestHandler


from django.test import SimpleTestCase
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite

from interface.models import Course, Submission, Assignment
from interface.admin import CourseAdmin, AssignmentAdmin


@pytest.fixture
def base_db_setup():
    user = User.objects.create_user("user", password="pw")

    ta = User.objects.create_user("ta", password="pw")
    course_admin = CourseAdmin(model=Course, admin_site=AdminSite())
    course_admin._add_new_ta(ta)

    super_user = User.objects.create_user(
        "root", password="pw", is_superuser=True, is_staff=True,
    )

    course = Course.objects.create(name="PC")
    course.teaching_assistants.set([ta])
    course.save()

    assignment = course.assignment_set.create(
        name="a0",
        max_score=100,
        deadline_soft=datetime(2050, 1, 1, tzinfo=timezone.utc),
        deadline_hard=datetime(2050, 1, 1, tzinfo=timezone.utc),
        repo_url="https://github.com/vmck/assignment",
        repo_path="pc-00",
    )

    return (super_user, ta, user, course, assignment)


@pytest.fixture
def STC():
    return SimpleTestCase()


@pytest.fixture
def mock_evaluate(monkeypatch):
    def evaluate_stub(path):
        pass

    monkeypatch.setattr(Submission, "evaluate", evaluate_stub)


@pytest.fixture
def mock_admin_assignment(monkeypatch):
    def run_moss_stub(assignment, request, queryset):
        return JsonResponse({"type": "run_moss"})

    def download_review_submissions_stub(assignment, request, queryset):
        return JsonResponse({"type": "download_review_submissions"})

    def download_all_submissions_stub(assignment, request, queryset):
        return JsonResponse({"type": "download_all_submissions"})

    monkeypatch.setattr(AssignmentAdmin, "run_moss", run_moss_stub)

    monkeypatch.setattr(
        AssignmentAdmin,
        "download_review_submissions",
        download_review_submissions_stub,
    )
    monkeypatch.setattr(
        AssignmentAdmin,
        "download_all_submissions",
        download_all_submissions_stub,
    )


@pytest.fixture
def mock_config(monkeypatch):
    ADDR = "10.66.60.1"
    PORT = 5000

    class Server:
        def __init__(self):
            self.server = HTTPServer((ADDR, PORT), SimpleHTTPRequestHandler,)

        def start_server(self):
            thread = threading.Thread(
                target=self.server.serve_forever, daemon=True,
            )
            thread.start()

        def stop_server(self):
            self.server.shutdown()
            self.server.server_close()

    def url_for(self, filename):
        return f"http://{ADDR}:{PORT}/testsuite/{filename}"

    monkeypatch.setattr(Assignment, "url_for", url_for)

    return Server()
