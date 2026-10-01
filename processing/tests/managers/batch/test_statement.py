from unittest.mock import patch

from processing.models.tags import StatementTag


def _session_day_tag(date_id: str) -> StatementTag:
    # Mirrors what the EP scraper writes: one session-day tag with a placeholder id.
    return StatementTag(
        chamberName="european-parliament", termId="9", sessionId="1", dateId=date_id, statementId="-"
    )


def test_european_parliament_find_payload_dedups_by_session_day(batch_manager_scrape_statement):
    manager = batch_manager_scrape_statement

    to_process = [_session_day_tag("2022-02-16"), _session_day_tag("2022-02-17")]
    previously_processed = [_session_day_tag("2022-02-16")]

    with patch.object(manager, "get_payload_tags_to_process", return_value=to_process), \
            patch.object(manager, "get_payload_previously_processed", return_value=previously_processed):
        diff = manager.find_payload(payload_id="any")

    # Only the new session-day survives, and it re-validates as a StatementTag.
    assert [tag.date_id for tag in diff] == ["2022-02-17"]
    assert all(isinstance(tag, StatementTag) for tag in diff)
