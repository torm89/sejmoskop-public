import json
import logging
from unittest.mock import MagicMock, patch

import requests

from processing.utils.log_forwarding import (
    MAX_CONSECUTIVE_FAILURES,
    VictoriaLogsHandler,
    attach_log_forwarding,
)

URL = "https://ingest.test/insert/jsonline"
TOKEN = "test-token"


def _record(message="hello"):
    return logging.LogRecord(
        name="test", level=logging.INFO, pathname=__file__, lineno=1, msg=message, args=(), exc_info=None
    )


def _response(status_code):
    response = MagicMock()
    response.status_code = status_code
    if status_code >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(str(status_code))
    return response


@patch("processing.utils.log_forwarding.requests.post")
def test_emit_posts_the_expected_request(mock_post):
    mock_post.return_value = _response(200)

    VictoriaLogsHandler(url=URL, token=TOKEN).emit(_record("hello"))

    _, kwargs = mock_post.call_args
    assert kwargs["headers"]["Authorization"] == f"Bearer {TOKEN}"
    assert kwargs["headers"]["Content-Type"] == "application/stream+json"
    assert kwargs["verify"] is False
    assert kwargs["data"].endswith("\n")

    body = json.loads(kwargs["data"])
    assert body["_msg"] == "hello"
    assert body["service"] == "processing"
    assert body["level"] == "info"


@patch("processing.utils.log_forwarding.requests.post")
def test_breaker_opens_after_consecutive_error_responses(mock_post):
    # requests does not raise on 4xx/5xx, so without raise_for_status a rejected
    # POST (e.g. a bad token) would count as a success and never open the breaker.
    mock_post.return_value = _response(401)
    handler = VictoriaLogsHandler(url=URL, token="wrong")

    for _ in range(MAX_CONSECUTIVE_FAILURES + 5):
        handler.emit(_record())

    assert mock_post.call_count == MAX_CONSECUTIVE_FAILURES


@patch("processing.utils.log_forwarding.requests.post")
def test_breaker_opens_after_consecutive_connection_errors(mock_post):
    mock_post.side_effect = requests.ConnectionError("host down")
    handler = VictoriaLogsHandler(url=URL, token=TOKEN)

    for _ in range(MAX_CONSECUTIVE_FAILURES + 5):
        handler.emit(_record())

    assert mock_post.call_count == MAX_CONSECUTIVE_FAILURES


@patch("processing.utils.log_forwarding.requests.post")
def test_success_resets_the_failure_count(mock_post):
    # A single success between failures keeps the breaker closed.
    failing, ok = _response(500), _response(200)
    mock_post.side_effect = [failing, failing, ok, failing, failing, ok, failing]
    handler = VictoriaLogsHandler(url=URL, token=TOKEN)

    for _ in range(7):
        handler.emit(_record())

    assert mock_post.call_count == 7


@patch("processing.utils.log_forwarding.requests.post")
def test_emit_never_raises_when_the_host_fails(mock_post):
    mock_post.side_effect = requests.ConnectionError("host down")

    VictoriaLogsHandler(url=URL, token=TOKEN).emit(_record())  # fail-open: must not raise


def test_attach_log_forwarding_without_env_adds_no_handler(monkeypatch):
    monkeypatch.delenv("LOG_INGEST_URL", raising=False)
    monkeypatch.delenv("LOG_INGEST_TOKEN", raising=False)

    logger = logging.getLogger("test-log-forwarding-no-env")
    logger.handlers = []

    attach_log_forwarding(logger)

    assert logger.handlers == []


def test_attach_log_forwarding_with_env_adds_the_handler(monkeypatch):
    monkeypatch.setenv("LOG_INGEST_URL", URL)
    monkeypatch.setenv("LOG_INGEST_TOKEN", TOKEN)

    logger = logging.getLogger("test-log-forwarding-with-env")
    logger.handlers = []

    attach_log_forwarding(logger)

    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], VictoriaLogsHandler)
