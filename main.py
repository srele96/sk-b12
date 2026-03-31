from dotenv import load_dotenv
from datetime import datetime
import requests
import os
import hmac
import json
import hashlib

load_dotenv()

KEY_DATA_URL = "DATA_URL"
KEY_DATA_NAME = "DATA_NAME"
KEY_DATA_EMAIL = "DATA_EMAIL"
KEY_DATA_RESUME_LINK = "DATA_RESUME_LINK"
KEY_DATA_REPOSITORY_LINK = "DATA_REPOSITORY_LINK"
KEY_DATA_ACTION_RUN_LINK = "DATA_ACTION_RUN_LINK"
KEY_DATA_SHA_HMAC_SECRET = 'DATA_SHA_HMAC_SECRET'

KEY_GITHUB_RUN_ID = 'GITHUB_RUN_ID'

VARS = [
    KEY_DATA_URL,
    KEY_DATA_NAME,
    KEY_DATA_EMAIL,
    KEY_DATA_RESUME_LINK,
    KEY_DATA_REPOSITORY_LINK,
    KEY_DATA_ACTION_RUN_LINK,
    KEY_GITHUB_RUN_ID,
    KEY_DATA_SHA_HMAC_SECRET
]


def ensureVarIsDefined(value=None):
    assert os.getenv(value) is not None, f"Missing required variable: {value}"


def ensureAllVarsAreDefined():
    for var in VARS:
        ensureVarIsDefined(var)


def computeDigest(data):
    jsonData = json.dumps(data)

    UTF_8 = 'utf-8'
    secretBytes = os.getenv(KEY_DATA_SHA_HMAC_SECRET).encode(UTF_8)
    messageBytes = jsonData.encode(UTF_8)
    print(f"jsonData:\n\n{jsonData}\n\n")
    digest = hmac.new(secretBytes, messageBytes, hashlib.sha256).hexdigest()

    return digest


def assertExpectedDigest():
    data = {
        'timestamp': "2026-01-06T16:59:37.571Z",
        'name': "Your name",
        'email': "you@example.com",
        'resume_link': "https://pdf-or-html-or-linkedin.example.com",
        'repository_link': "https://link-to-github-or-other-forge.example.com/your/repository",  # noqa: 501
        'action_run_link': "https://link-to-github-or-another-forge.example.com/your/repository/actions/runs/run_id"  # noqa: 501
    }

    # Expected digest to confirm correctness of the code
    # https://job-boards.greenhouse.io/b12/jobs/7544356
    expectedDigest = 'c5db257a56e3c258ec1162459c9a295280871269f4cf70146d2c9f1b52671d45'  # noqa: 501

    digest = computeDigest(data)

    assert digest is expectedDigest, (
        f"Unexpected signature. Received: {digest}."
        f" Expected: {expectedDigest}"
    )


def submitApplication():
    # The body must follow requirements
    # https://job-boards.greenhouse.io/b12/jobs/7544356
    #
    # Timestamp ISO 8601
    # https://pynative.com/python-iso-8601-datetime/
    today = datetime.now()
    iso_date = today.isoformat()
    data = {
        'timestamp': iso_date,
        'name': os.getenv(KEY_DATA_NAME),
        'email': os.getenv(KEY_DATA_EMAIL),
        'resume_link': os.getenv(KEY_DATA_RESUME_LINK),
        'repository_link': os.getenv(KEY_DATA_REPOSITORY_LINK),
        'action_run_link': os.getenv(KEY_GITHUB_RUN_ID)
    }

    jsonData = json.dumps(data)

    digest = computeDigest(data)
    response = requests.post(
        os.getenv(KEY_DATA_URL),
        data=jsonData, headers={
            'X-Signature-256': f'sha256={digest}'
        }
    )
    if response.ok:
        print("ok", response.json())
    else:
        print("Error", response.status_code)


def main():
    ensureAllVarsAreDefined()
    assertExpectedDigest()
    submitApplication()


if __name__ == "__main__":
    main()
