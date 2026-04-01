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

KEY_SUBMIT_APPLICATION = 'SUBMIT_APPLICATION'
KEY_DEBUG = 'DEBUG'

VARS = [
    KEY_DATA_URL,
    KEY_DATA_NAME,
    KEY_DATA_EMAIL,
    KEY_DATA_RESUME_LINK,
    KEY_DATA_REPOSITORY_LINK,
    KEY_DATA_ACTION_RUN_LINK,
    KEY_DATA_SHA_HMAC_SECRET,
    KEY_SUBMIT_APPLICATION,
    KEY_DEBUG
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
DATA_ACTION_RUN_LINK = os.getenv(KEY_DATA_ACTION_RUN_LINK)


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

DEBUG = strToBool(os.getenv(KEY_DEBUG))

# ENVIRONMENT VARIABLES =======================================================
# =============================================================================


# =============================================================================
# IMPLEMENTATION ==============================================================


class SimpleLogger:
    @staticmethod
    def logError(value: str):
        printf(f"**** SK-B12 ERROR **** {value}")

    @staticmethod
    def logMessage(value: str):
        print(f"**** SK-B12 MESSAGE **** {value}")

    @staticmethod
    def logDebug(value: str):
        if DEBUG:
            print(f"**** SK-B12 DEBUG **** {value}")

    @staticmethod
    def logStr(value: str):
        return f"-- {value} -- "

    @staticmethod
    def calledFrom(value: str):
        return f"({value}): "

    @staticmethod
    def jsonDumps(data: dict):
        return json.dumps(data, separators=(',', ':'), sort_keys=True)


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

    fnName = "assertExpectedDigest"
    SimpleLogger.logDebug(
        f"{SimpleLogger.calledFrom(fnName)} "
        f"{SimpleLogger.logStr("data")} "
        f"{SimpleLogger.jsonDumps(data)}"
    )

    # Expected digest to confirm correctness of the code
    # https://job-boards.greenhouse.io/b12/jobs/7544356
    expectedDigest = 'c5db257a56e3c258ec1162459c9a295280871269f4cf70146d2c9f1b52671d45'  # noqa: 501

    SimpleLogger.logDebug(
        f"{SimpleLogger.calledFrom(fnName)} "
        f"{SimpleLogger.logStr("expectedDigest")} "
        f"{expectedDigest}"
    )

    digest = computeDigest(data)

    SimpleLogger.logDebug(
        f"{SimpleLogger.calledFrom(fnName)} "
        f"{SimpleLogger.logStr("digest")} "
        f"{digest}"
    )

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
        'action_run_link': DATA_ACTION_RUN_LINK
    }

    fnName = "submitApplication"
    SimpleLogger.logDebug(
        f"{SimpleLogger.calledFrom(fnName)} "
        f"{SimpleLogger.logStr("data")} "
        f"{SimpleLogger.jsonDumps(data)}"
    )

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
    if response.ok or response.status_code == 200:
        SimpleLogger.logMessage(
            f"{SimpleLogger.calledFrom(fnName)}"
            f"{SimpleLogger.logStr("SUCCESS")}"
            f"{response.json()}"
        )
    else:
        SimpleLogger.logError(
            f"{SimpleLogger.calledFrom(fnName)}"
            f"{SimpleLogger.logStr("Request failed with status code")}"
            f"{response.status_code}"
        )
        print("Error", response.status_code)

# IMPLEMENTATION ==============================================================
# =============================================================================


def main():
    assertExpectedDigest()

    if SUBMIT_APPLICATION:
        submitApplication()


if __name__ == "__main__":
    main()
