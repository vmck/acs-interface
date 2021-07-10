import logging
from urllib.parse import urljoin

import requests
from django.conf import settings

from interface.backend.submission.evaluator.abstract import Evaluator

log = logging.getLogger(__name__)


class VMCK(Evaluator):
    @staticmethod
    def evaluate(submission):
        callback = f"submission/{submission.pk}/done?token={submission.generate_jwt()}"

        options = {
            "image_path": submission.assignment.image_path,
            "cpus": int(submission.assignment.vm_options["nr_cpus"]),
            "memory": int(submission.assignment.vm_options["memory"]),
            "name": f"{submission.assignment.full_code} submission #{submission.pk}",
            "restrict_network": True,
            "backend": settings.EVALUATOR_BACKEND,
            "manager": {
                "vagrant_tag": settings.MANAGER_TAG,
                "memory_mb": settings.MANAGER_MEMORY,
                "cpu_mhz": settings.MANAGER_MHZ,
            },
            "env": {
                "VMCK_ARCHIVE_URL": submission.get_url(),
                "VMCK_SCRIPT_URL": submission.get_script_url(),
                "VMCK_ARTIFACT_URL": submission.get_artifact_url(),
                "VMCK_CALLBACK_URL": urljoin(settings.ACS_INTERFACE_ADDRESS, callback),
            },
        }

        log.debug("Submission #%s config is done", submission.pk)
        log.debug("Callback: %s", options["env"]["VMCK_CALLBACK_URL"])

        response = requests.post(
            urljoin(settings.VMCK_API_URL, "jobs"),
            json=options,
        )

        log.debug("Submission's #%s VMCK response:\n%s", submission.pk, response)

        return response.json()["id"]

    @staticmethod
    def update(submission):
        response = requests.get(
            urljoin(
                settings.VMCK_API_URL,
                f"jobs/{submission.evaluator_job_id}",
            ),
        )
        try:
            json_response = response.json()
            return json_response["state"]
        except Exception:
            log.exception("JSON conversion error")
            return "error"
