from tidelift import TideliftUniqueIssue
import requests
import json
import copy

class JiraTideliftUniqueIssueRenderer:
    """
    Modify the methods in this class to define how Tidelift violation data
    is written to your Jira issues.
    """
    def __init__(self, tidelift_unique_issue: TideliftUniqueIssue):
        self.tidelift_unique_issue = tidelift_unique_issue

    def to_json_create(self):
        return {
            "fields": {
                "summary": self.summary(),
                "description": self.description()
            }
        }

    def to_json_update(self):
        return {
            "fields": {
                "description": self.description()
            }
        }

    def summary(self):
        first_report_entry = self.tidelift_unique_issue.violations[0]

        return " - ".join([part for part in self.tidelift_unique_issue.unique_key_parts])

    def description(self):
        output = {
            "version": 1,
            "type": "doc",
            "content": []
        }

        for violation in self.tidelift_unique_issue.violations:
            # This is an extremely quick and dirty way to show how data from
            # report objects can be placed into a Jira issue.
            for key in [
                'violation_type',
                'violation_description',
                'dependency_chain',
                'action',
                'violation_link'
            ]:
                output["content"].append(
                    {
                        "type": "paragraph",
                        "content": [{
                            "type": "text",
                            "text": f"{key}: {violation[key]}"
                        }]
                    }
                )
            output['content'].append(
                    {
                        "type": "paragraph",
                        "content": [{
                            "type": "text",
                            "text": "---------------------------------------"
                        }]
                    }
            )

        return output

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

class JiraConfig:
    def __init__(self, config: dict):
        self.config = config

    def api_base(self):
        return self.config['api_base']

    def unique_field_name(self):
        return self.config['unique_field_name']

    def project_id(self):
        return self.config['project_id']

    def issue_type(self):
        return self.config['issue_type']

class JiraService:
    def __init__(self, config: JiraConfig, auth):
        self.config = config
        self.auth = auth

    def build_unique_field_service(self):
        response = requests.request(
            "GET",
            f"{self.config.api_base()}/field",
            headers = headers,
            auth = self.auth
        )

        fields = json.loads(response.text)
        unique_field = [field for field in fields if field["name"] == self.config.unique_field_name()]
        if len(unique_field) == 0:
            raise Exception(f"'{self.config.unique_field_name()}' not found in the remote Jira issue fields list. Do you have the correct field name configured?")
        unique_field = unique_field[0]

        return JiraUniqueFieldService(
            config = self.config,
            unique_field = unique_field,
            auth = self.auth
        )

class JiraUniqueFieldService:
    def __init__(self, config: JiraConfig, unique_field: dict, auth):
        self.config = config
        self.unique_field = unique_field
        self.auth = auth

    def search(self, unique_key) -> dict | None:
        response = requests.request(
            "GET",
            f"{self.config.api_base()}/search",
            headers = headers,
            auth = self.auth,
            params = {
                "jql": f"'{self.unique_field['name']}[Short text]' ~ '{unique_key}'"
            }
        )

        existing_issues = json.loads(response.text)
        existing_issue = None
        if existing_issues["total"] > 0:
            existing_issue = existing_issues["issues"][0]

        return existing_issue

    def update(self, existing_issue_id, payload):
        response = requests.request(
            "PUT",
            f"{self.config.api_base()}/issue/{existing_issue_id}",
            data = json.dumps(payload),
            headers = headers,
            auth = self.auth
        )

        return response

    def create(self, payload, unique_hash):
        payload = copy.deepcopy(payload)
        payload["fields"][str(self.unique_field['id'])] = unique_hash
        payload["fields"]["project"] = { "key": self.config.project_id() }
        payload["fields"]["issuetype"] = { "id": self.config.issue_type() }

        response = requests.request(
            "POST",
            f"{self.config.api_base()}/issue",
            data = json.dumps(payload),
            headers = headers,
            auth = self.auth
        )

        return response

