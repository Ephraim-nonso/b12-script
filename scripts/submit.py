import json
import hmac
import hashlib
import datetime
import os
import sys
import requests

B12_URL = "https://b12.io/apply/submission"
SIGNING_SECRET = b"hello-there-from-b12"


def iso8601_timestamp():
    return (
        datetime.datetime.now(datetime.UTC)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        print(f"Missing required environment variable: {name}", file=sys.stderr)
        sys.exit(1)
    return value


def main():
    payload = {
        "action_run_link": required_env("GITHUB_RUN_URL"),
        "email": required_env("B12_EMAIL"),
        "name": required_env("B12_NAME"),
        "repository_link": required_env("B12_REPOSITORY_LINK"),
        "resume_link": required_env("B12_RESUME_LINK"),
        "timestamp": iso8601_timestamp(),
    }

    body = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    signature = hmac.new(
        SIGNING_SECRET,
        body,
        hashlib.sha256,
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-Signature-256": f"sha256={signature}",
    }

    response = requests.post(B12_URL, data=body, headers=headers)

    if response.status_code != 200:
        print("Submission failed:", response.status_code, response.text, file=sys.stderr)
        sys.exit(1)

    receipt = response.json().get("receipt")
    print("Submission successful")
    print("Receipt:", receipt)


if __name__ == "__main__":
    main()