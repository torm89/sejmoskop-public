import logging
import os
import time

import requests

logger = logging.getLogger()
logger.setLevel("INFO")

CONFIG_TAG_TEMPLATE = "sejmoskop-{env}-config"
TERM_TAG_TEMPLATE = "sejmoskop-{env}-term-{chamber_name}-{term_id}"

# Keep attempts x (timeout + backoff) under the Lambda timeout so all retries actually run
# before the function is killed: 4 x 10s + (2 + 4 + 8)s backoff = 54s < 60s.
REQUEST_TIMEOUT_SECONDS = 10
REQUEST_MAX_ATTEMPTS = 4
REQUEST_BACKOFF_BASE_SECONDS = 2


def collect_tags(env, chambers):
    # The config tag is always revalidated once per run; it covers global, term-independent pages.
    tags = [CONFIG_TAG_TEMPLATE.format(env=env)]

    for chamber in chambers:
        # On a caught chamber failure the upstream state replaces UpdateOutput with the error object,
        # so there is no Output and nothing changed to revalidate for this chamber.
        output = chamber.get("UpdateOutput", {}).get("Output")
        if not output:
            continue

        chamber_input = chamber["UpdateOutput"]["Input"]
        scrape_and_process = output["ScrapeAndProcessOutput"]

        members = scrape_and_process[0]["MembersProcessingOutput"]
        votings = scrape_and_process[1]["VotingsProcessingOutput"]
        groups = scrape_and_process[2]["GroupsProcessingOutput"]
        # Statements are served dynamically from OpenSearch, so they never invalidate a term page.

        if members > 0 or votings > 0 or groups > 0:
            tags.append(TERM_TAG_TEMPLATE.format(
                env=env,
                chamber_name=chamber_input["chamberName"],
                term_id=chamber_input["termId"],
            ))

    return tags


def revalidate(api_url, api_token, tags):
    for attempt in range(1, REQUEST_MAX_ATTEMPTS + 1):
        try:
            response = requests.post(
                f"{api_url}/cache/revalidate",
                headers={"Authorization": api_token, "content-type": "application/json"},
                json={"tags": tags},
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return
        except requests.RequestException as error:
            logger.warning(f"Cache revalidation attempt {attempt}/{REQUEST_MAX_ATTEMPTS} failed: {error}")
            if attempt == REQUEST_MAX_ATTEMPTS:
                raise
            time.sleep(REQUEST_BACKOFF_BASE_SECONDS ** attempt)


def handler(event, context):
    env = os.environ["SJ_ENV"]
    api_url = os.environ["SEJMOSKOP_WEB_API_URL"]
    api_token = os.environ["SEJMOSKOP_WEB_API_TOKEN"]

    tags = collect_tags(env=env, chambers=event["chambers"])

    logger.info(f"Revalidating cache tags: {tags}")
    revalidate(api_url=api_url, api_token=api_token, tags=tags)

    return {"revalidatedTags": tags}


if __name__ == "__main__":
    handler({"chambers": []}, None)
