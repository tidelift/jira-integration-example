#!/usr/bin/env python3

import os
from dotenv import load_dotenv

import yaml
import json

from requests.auth import HTTPBasicAuth

from jira import JiraService, JiraConfig, JiraTideliftUniqueIssueRenderer
from tidelift import TideliftConfig, TideliftService, generate_unique_tidelift_issues_from_report

load_dotenv()

with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

tl_service = TideliftService(
    api_key = os.environ['TIDELIFT_API_KEY'],
    config = TideliftConfig(config['tidelift'])
)

# New reports are generated daily for paying subscribers.
report = tl_service.all_projects_violations_report()["report"]

jira_service = JiraService(
    config = JiraConfig(config['jira']),
    auth = HTTPBasicAuth(os.environ["JIRA_EMAIL"], os.environ["JIRA_TOKEN"])
)
jira_unique_field_service = jira_service.build_unique_field_service()

unique_key_fields = config['tidelift']['unique_key_parts']

tidelift_unique_issues = generate_unique_tidelift_issues_from_report(
    report,
    unique_key_fields = unique_key_fields
)

totals = {
    "processed": 0,
    "added": 0,
    "updated": 0
}

for tidelift_unique_issue in tidelift_unique_issues:
    unique_hash = tidelift_unique_issue.unique_hash()
    renderer = JiraTideliftUniqueIssueRenderer(tidelift_unique_issue)

    # if there is one, update that one's description
    # otherwise create a new story
    existing_issue = jira_unique_field_service.search(unique_hash)

    totals["processed"] += 1

    if existing_issue:
        jira_unique_field_service.update(
            existing_issue_id = existing_issue['id'],
            payload = renderer.to_json_update()
        )

        print(f"{existing_issue['id']} Updated")

        totals["updated"] += 1
    else:
        response = jira_unique_field_service.create(
            payload = renderer.to_json_create(),
            unique_hash = unique_hash
        )

        print(json.dumps(json.loads(response.text), sort_keys = True))

        totals["added"] += 1

print(f"Totals: {totals['processed']} total, {totals['added']} added, {totals['updated']} updated")
