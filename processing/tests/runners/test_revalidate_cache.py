import importlib.util
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


def _load_handler_module():
    # The handler lives under a directory named `lambda`, which is a Python keyword and cannot be
    # imported as a package, so load it directly by file path instead.
    here = Path(__file__).resolve()
    root = next(p for p in here.parents if (p / "processing" / "runners").is_dir())
    module_path = root / "processing" / "runners" / "aws" / "lambda" / "revalidate_cache" / "lambda_function.py"

    spec = importlib.util.spec_from_file_location("revalidate_cache_lambda", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


revalidate_cache = _load_handler_module()


def _chamber(chamber_name, term_id, members=0, votings=0, groups=0, statements=0):
    return {
        "UpdateOutput": {
            "Input": {"chamberName": chamber_name, "termId": term_id},
            "Output": {
                "ScrapeAndProcessOutput": [
                    {"MembersProcessingOutput": members},
                    {"VotingsProcessingOutput": votings},
                    {"GroupsProcessingOutput": groups},
                    {"StatementsProcessingOutput": statements},
                ]
            },
        }
    }


def test_config_tag_is_always_present():
    tags = revalidate_cache.collect_tags(env="prod", chambers=[])

    assert tags == ["sejmoskop-prod-config"]


def test_term_tag_added_when_members_votings_or_groups_changed():
    chambers = [_chamber("sejm", "10", votings=3)]

    tags = revalidate_cache.collect_tags(env="prod", chambers=chambers)

    assert tags == ["sejmoskop-prod-config", "sejmoskop-prod-term-sejm-10"]


def test_statements_only_change_does_not_revalidate_term():
    chambers = [_chamber("sejm", "10", statements=5)]

    tags = revalidate_cache.collect_tags(env="prod", chambers=chambers)

    assert tags == ["sejmoskop-prod-config"]


def test_caught_chamber_without_output_is_skipped():
    chambers = [{"UpdateOutput": {"Error": "States.TaskFailed", "Cause": "boom"}}]

    tags = revalidate_cache.collect_tags(env="prod", chambers=chambers)

    assert tags == ["sejmoskop-prod-config"]


def test_multiple_chambers_collect_their_own_term_tags():
    chambers = [
        _chamber("sejm", "10", members=1),
        _chamber("senat", "11"),
        _chamber("european-parliament", "10", groups=2),
    ]

    tags = revalidate_cache.collect_tags(env="dev", chambers=chambers)

    assert tags == [
        "sejmoskop-dev-config",
        "sejmoskop-dev-term-sejm-10",
        "sejmoskop-dev-term-european-parliament-10",
    ]


def test_revalidate_raises_after_exhausting_attempts():
    with patch.object(revalidate_cache.requests, "post", side_effect=revalidate_cache.requests.RequestException("down")), \
            patch.object(revalidate_cache.time, "sleep", Mock()):
        with pytest.raises(revalidate_cache.requests.RequestException):
            revalidate_cache.revalidate(api_url="https://x/api", api_token="t", tags=["a"])


def test_revalidate_posts_tags_and_succeeds():
    response = Mock()
    with patch.object(revalidate_cache.requests, "post", return_value=response) as post:
        revalidate_cache.revalidate(api_url="https://x/api", api_token="secret", tags=["a", "b"])

    post.assert_called_once()
    assert post.call_args.kwargs["json"] == {"tags": ["a", "b"]}
    assert post.call_args.kwargs["headers"]["Authorization"] == "secret"
    response.raise_for_status.assert_called_once()
