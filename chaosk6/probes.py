import subprocess
import os
import json

from logzero import logger
from pathlib import Path

__all__ = ["http"]


def http(
    endpoint: str,
    method: str = "GET",
    status: int = 200,
    body: str = "",
    headers: dict = {},
):
    """
    Probe an endpoint to make sure it responds to an http request
    with the expected HTTP status code. Depending on the endpoint and your
    payload, this action might be destructive. Use with caution.

    Parameters
    ----------
    endpoint : str
        The URL to the endpoint to probe
    method : str
        A valid http request method name, like GET, POST, PUT, DELETE, OPTIONS, or PATCH
    status : int
        The expected HTTP Response status code.
    """
    if status < 100 or status > 999:
        raise Exception("Invalid HTTP Response status code expection")
    if method.lower() not in ["get", "post", "put", "patch", "delete", "options"]:
        raise Exception("Invalid HTTP Request method")
    if endpoint == None:
        raise Exception("Endpoint is a required argument")

    env = dict(
        **os.environ,
        CHAOS_K6_URL=endpoint,
        CHAOS_K6_METHOD=method,
        CHAOS_K6_STATUS=str(status),
        CHAOS_K6_BODY=body,
        CHAOS_K6_HEADERS=json.dumps(headers)
    )

    scriptDir = os.path.dirname(os.path.realpath(__file__))

    cmd = ["k6", "run", "{}/scripts/probe.js".format(scriptDir)]

    with subprocess.Popen(
        cmd, env=env, stderr=subprocess.STDOUT, stdout=subprocess.PIPE
    ) as p:
        try:
            p.wait(10)
        except subprocess.TimeoutExpired:
            assert p.returncode is None
        return p.returncode == 0