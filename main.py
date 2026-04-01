from dotenv import load_dotenv
from datetime import datetime
import requests
import os
import hmac
import json
import hashlib

# =============================================================================
# ENVIRONMENT VARIABLES =======================================================

load_dotenv()

KEY_DATA_URL = "DATA_URL"
KEY_DATA_NAME = "DATA_NAME"
KEY_DATA_EMAIL = "DATA_EMAIL"
KEY_DATA_RESUME_LINK = "DATA_RESUME_LINK"
KEY_DATA_REPOSITORY_LINK = "DATA_REPOSITORY_LINK"
KEY_DATA_ACTION_RUN_LINK = "DATA_ACTION_RUN_LINK"
KEY_DATA_SHA_HMAC_SECRET = 'DATA_SHA_HMAC_SECRET'

# Figure out if i can retrieve correct github run id automatically, or i need
# to use some API call
# https://stackoverflow.com/questions/76464269/how-to-rerun-a-github-action-workflow-from-the-command-line-and-have-the-status/76465815#76465815
KEY_GITHUB_RUN_ID = 'GITHUB_RUN_ID'

KEY_SUBMIT_APPLICATION = 'SUBMIT_APPLICATION'

VARS = [
    KEY_DATA_URL,
    KEY_DATA_NAME,
    KEY_DATA_EMAIL,
    KEY_DATA_RESUME_LINK,
    KEY_DATA_REPOSITORY_LINK,
    KEY_DATA_ACTION_RUN_LINK,
    KEY_GITHUB_RUN_ID,
    KEY_DATA_SHA_HMAC_SECRET,
    KEY_SUBMIT_APPLICATION
]


def ensureVarIsDefined(value=None):
    assert os.getenv(value) is not None, f"Missing required variable: {value}"


def ensureAllVarsAreDefined(vars):
    for var in vars:
        ensureVarIsDefined(var)


ensureAllVarsAreDefined(VARS)

# Retrieve injected variables

# Clean up whitespaces to ensure consiste SHA digest
DATA_SHA_HMAC_SECRET = os.getenv("DATA_SHA_HMAC_SECRET", "").strip()

DATA_URL = os.getenv(KEY_DATA_URL)
DATA_NAME = os.getenv(KEY_DATA_NAME)
DATA_EMAIL = os.getenv(KEY_DATA_EMAIL)
DATA_RESUME_LINK = os.getenv(KEY_DATA_RESUME_LINK)
DATA_REPOSITORY_LINK = os.getenv(KEY_DATA_REPOSITORY_LINK)

GITHUB_RUN_ID = os.getenv(KEY_GITHUB_RUN_ID)


def strToBool(value: str):
    stripped = value.lower().strip()
    _true = "true"
    _false = "false"
    if stripped == _true:
        return True
    if stripped == _false:
        return False
    raise ValueError(f"Received invalid value. Expected {_true}"
                     f"or {_false}, received: {stripped}")


# The issue with dotenv is that every value is treated as a string
SUBMIT_APPLICATION = strToBool(os.getenv(KEY_SUBMIT_APPLICATION))

# ENVIRONMENT VARIABLES =======================================================
# =============================================================================


# =============================================================================
# IMPLEMENTATION ==============================================================

def getConsistentData(data):
    # Ensure consistent SHA digest
    return json.dumps(data, separators=(',', ':'), sort_keys=True)


def computeDigest(data):
    jsonData = getConsistentData(data)

    UTF_8 = 'utf-8'
    secretBytes = DATA_SHA_HMAC_SECRET.encode(UTF_8)
    messageBytes = jsonData.encode(UTF_8)
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

    assert digest == expectedDigest, (
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
        'name': DATA_NAME,
        'email': DATA_EMAIL,
        'resume_link': DATA_RESUME_LINK,
        'repository_link': DATA_REPOSITORY_LINK,
        'action_run_link': GITHUB_RUN_ID
    }

    jsonData = getConsistentData(data)

    digest = computeDigest(data)
    # TODO: Make submission blockable by default, to debug git workflow ID
    # retrieval
    response = requests.post(
        DATA_URL,
        data=jsonData, headers={
            'X-Signature-256': f'sha256={digest}',
            'Content-Type': 'application/json'
        }
    )
    if response.ok:
        print("ok", response.json())
    else:
        print("Error", response.status_code)

# IMPLEMENTATION ==============================================================
# =============================================================================


def main():
    assertExpectedDigest()

    if SUBMIT_APPLICATION:
        submitApplication()


if __name__ == "__main__":
    main()
