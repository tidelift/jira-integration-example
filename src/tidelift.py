import hashlib
import json
import requests
import pprint

class TideliftConfig:
    def __init__(self, config: dict):
        self.config = config

    def organization(self):
        return self.config['organization']

    def catalog(self):
        return self.config['catalog']

class TideliftService:
    def __init__(self, api_key: str, config: TideliftConfig):
        self.api_key = api_key
        self.config = config

    def headers(self):
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def all_projects_violations_report(self):
        url = f"https://api.tidelift.com/external-api/v1/{self.config.organization()}/reports/all_projects_violations?catalog_name={self.config.catalog()}"

        response = requests.request(
            "GET",
            url,
            headers = self.headers()
        )

        return json.loads(response.text)

class TideliftUniqueIssue:
    def __init__(self, unique_key_parts: list[str], violations: list[dict]):
        self.unique_key_parts = unique_key_parts
        self.violations = violations

    def unique_hash(self):
        hash = hashlib.sha256()
        for part in self.unique_key_parts:
            hash.update(part.encode())
        return hash.hexdigest()

import pprint

def process_grouped_violations_node(node, unique_key_parts = []) -> list[TideliftUniqueIssue]:
    result: list[TideliftUniqueIssue] = []

    for key in node:
        value = node[key]

        if isinstance(value, dict):
            result += process_grouped_violations_node(value, unique_key_parts + [key])
        else:
            result.append(
                TideliftUniqueIssue(
                    unique_key_parts = unique_key_parts + [key],
                    violations = node[key]
                )
            )

    return result

def generate_unique_tidelift_issues_from_report(report, unique_key_fields = None):
    if unique_key_fields is None or len(unique_key_fields) == 0:
        raise Exception('unique_key_fields must have at least one value')

    grouped_violations = {}
    last_unique_key_field = unique_key_fields[-1]

    for violation in report:
        current_location = grouped_violations

        for unique_key_field in unique_key_fields:
            violation_field_value = violation[unique_key_field]

            if unique_key_field == last_unique_key_field:
                if violation_field_value not in current_location:
                    current_location[violation_field_value] = []
                current_location[violation_field_value].append(violation)
            else:
                if violation_field_value not in current_location:
                    current_location[violation_field_value] = {}
                current_location = current_location[violation_field_value]

    tidelift_unique_issues: list[TideliftUniqueIssue] = []

    return process_grouped_violations_node(grouped_violations)

