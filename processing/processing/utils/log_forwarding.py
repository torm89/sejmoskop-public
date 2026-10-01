import json
import logging
import os

import requests

# Forward log records to VictoriaLogs, on top of the handlers that already ship
# logs to CloudWatch. Best-effort and fail-open: errors are swallowed, so
# logging never breaks the Batch job.
#
# Circuit breaker: after MAX_CONSECUTIVE_FAILURES failed POSTs in a row, assume
# the ingest host is down and stop forwarding for the rest of the run. A single
# success resets the counter.
#
# Active only when LOG_INGEST_URL and LOG_INGEST_TOKEN are set (injected into the
# Batch job definitions by Terraform). Without them no handler is attached, so
# local/dev runs stay silent.

SERVICE = "processing"
CONTENT_TYPE = "application/stream+json"
MAX_CONSECUTIVE_FAILURES = 3  # after this many POSTs fail in a row, give up for the run
# Per-request timeout; a slow or unreachable host counts as a failure toward the breaker.
REQUEST_TIMEOUT_SECONDS = 5


class VictoriaLogsHandler(logging.Handler):
    def __init__(self, url, token):
        super().__init__()
        self.url = url
        self.token = token
        self.failures = 0
        self._sending = False

    def emit(self, record):
        # Circuit open: the host failed too many times in a row, so give up.
        if self.failures >= MAX_CONSECUTIVE_FAILURES:
            return

        # Guard against feedback loops: our own POST may emit log records (e.g.
        # from the HTTP client), which would otherwise re-enter this handler.
        if self._sending:
            return

        self._sending = True
        try:
            line = json.dumps({
                "_msg": self.format(record),
                "service": SERVICE,
                "level": record.levelname.lower(),
                "job": os.environ.get("AWS_BATCH_JQ_NAME", ""),
            })
            response = requests.post(
                self.url,
                data=line + "\n",
                headers={"Authorization": f"Bearer {self.token}", "Content-Type": CONTENT_TYPE},
                # The ingest host uses a self-signed certificate, so verification is
                # skipped for this request only - never as a global TLS setting.
                # urllib3 warns about it once per process, which is left visible.
                verify=False,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            # requests does not raise on 4xx/5xx, so without this a rejected POST
            # (e.g. a bad token returning 401) would count as a success and the
            # breaker would never open.
            response.raise_for_status()
            self.failures = 0
        except Exception:
            self.failures += 1  # fail-open; the breaker trips after enough in a row
        finally:
            self._sending = False


def attach_log_forwarding(logger):
    url = os.environ.get("LOG_INGEST_URL")
    token = os.environ.get("LOG_INGEST_TOKEN")
    if not url or not token:
        return

    logger.addHandler(VictoriaLogsHandler(url=url, token=token))
