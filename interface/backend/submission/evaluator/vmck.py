import logging
from urllib.parse import urljoin

import requests
from django.conf import settings

from interface.backend.submission.evaluator.abstract import Evaluator

log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


class VMCK(Evaluator):
    def evaluate(submission):
        callback = (
            f"submission/{submission.pk}/done?"
            f"token={str(submission.generate_jwt(), encoding='latin1')}"
        )

        options = {}
        vm_options = submission.assignment.vm_options

        options["image_path"] = submission.assignment.image_path
        options["cpus"] = int(vm_options["nr_cpus"])
        options["memory"] = int(vm_options["memory"])

        name = f"{submission.assignment.full_code} submission #{submission.pk}"
        options["name"] = name
        options["restrict_network"] = True
        options["backend"] = settings.EVALUATOR_BACKEND

        options["manager"] = {}
        options["manager"]["vagrant_tag"] = settings.MANAGER_TAG
        options["manager"]["memory_mb"] = settings.MANAGER_MEMORY
        options["manager"]["cpu_mhz"] = settings.MANAGER_MHZ

        options["env"] = {}
        options["env"]["VMCK_ARCHIVE_URL"] = submission.get_url()
        options["env"]["VMCK_SCRIPT_URL"] = submission.get_script_url()
        options["env"]["VMCK_ARTIFACT_URL"] = submission.get_artifact_url()
        options["env"]["VMCK_CALLBACK_URL"] = urljoin(
            settings.ACS_INTERFACE_ADDRESS, callback,
        )

        log.debug("Submission #%s config is done", submission.pk)
        log.debug("Callback: %s", options["env"]["VMCK_CALLBACK_URL"])

        response = requests.post(
            urljoin(settings.VMCK_API_URL, "jobs"), json=options
        )

        log.debug(
            "Submission's #%s VMCK response:\n%s", submission.pk, response
        )

        return response.json()["id"]

    def update(submission):
        response = requests.get(
            urljoin(
                settings.VMCK_API_URL, f"jobs/{submission.evaluator_job_id}"
            )
        )
        try:
            json_response = response.json()
            return json_response["state"]
        except Exception as e:
            log.debug(f"JSON conversion error: {e}")
            return "error"
