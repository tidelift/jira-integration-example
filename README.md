# Creating Jira issues from the Tidelift All Projects Violations JSON Report

This code uses the Tidelift All Projects Violations JSON report to create or
update issues on a specific Jira board for a single Tidelift catalog. In
this example:

* All violations are grouped by **violating purl** and **project name**.
* The violation details are added to the issue description in a simplistic
  but actionable way.
* A custom short text issue field stores a hash of the violating purl and
  project name to ensure issue uniqueness. If the individual violations
  that group with that set of fields change, the descriptions of the
  issues will be updated.

You can change the top-level report fields used to create the issues by
modifying `config.yml` and changing `tidelift.unique_key_parts`. You can
see all the available report fields in [the Tidelift docs](https://support.tidelift.com/hc/en-us/articles/24883174701332-All-projects-violations-report#h_01HSKW9P4CXD8TNZ4PV1D199DK).
If you want to modify the title and contents of the Jira issue, examine
`JiraTideliftUniqueIssueRenderer` and the `summary` and `description`
methods.

This is not a full Jira integration! Use this code as a base or inspiration
to start building your own unique Jira workflow.

## Requirements

* Python 3
* Tidelift Management subscription with:
  * A [catalog with enabled standards](https://support.tidelift.com/hc/en-us/articles/4406286196244-Introduction-to-catalog-standards)
  * At least one [project](https://support.tidelift.com/hc/en-us/articles/4406286154004-About-projects-and-bill-of-materials)
  * At least one [saved alignment in that project with a violation](https://support.tidelift.com/hc/en-us/articles/7113535394452-Tracking-your-software-dependencies-with-Tidelift#h_01HXHSMHD6A7PPMFNQCZX4GF7R)
    * If you need an example that will trigger a violation, ensure the
      [Deprecation standard](https://support.tidelift.com/hc/en-us/articles/4406293305108-Deprecated-packages-standard)
      is enabled on your catalog and upload
      `example-manifest/package.json` and `example-manifest/package-lock.json`
      as a new alignment. The one direct dependency
      `request` [has been deprecated since 2020](https://www.npmjs.com/package/request)
      and will trigger a violation.
* Atlassian Jira cloud account
  * This may work with on-prem but I can't test that right now!
  * A Jira board with:
    * A single **Short text** issue field named
      `Violating purl and project hash` (the default value of
      `jira.unique_field_name`)

## Instructions

* Create a new virtual environment: `python3 -m venv .venv`
* Load the virtual environment: `. .venv/bin/activate`
* Install dependencies: `pip3 install -r requirements.txt`
* Copy `env.sample` to `.env`
* Populate `.env` with your Jira and Tidelift credentials
* Copy `config.yml.sample` to `config.yml`
* Customize `config.yml` for your Jira project and Tidelift preferences
* In Jira, create a new short text Issue field that matches `jira.unique_field_name`
* Run `python3 ./import.py`
