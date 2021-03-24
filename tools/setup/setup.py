#!/usr/bin/env python3
from jinja2 import Environment
from jinja2 import FileSystemLoader

organisation_name = input("Enter the company name (e.g. Acme Limited): ")
package_author = input("Your full name (e.g. Joe Smith): ")
github_org = input("The GitHub Organisation (e.g. AcmeLtd): ")
package_repo_url = input("The GitHub URL (e.g. git@github.com:acme/iac.git): ")
package_name = input("The package name (e.g. acme-iac-project): ")
package_description = input("The package description: ")
aws_region = input("The AWS region (e.g. eu-west-2): ")
aws_account_id = input("The AWS Account identifier (e.g. 600123456789): ")
tfstate_bucket_name = input("The Terraform bucket prefix (e.g. acme-tfstate): ")

env = Environment(
    loader=FileSystemLoader("."), autoescape=True, keep_trailing_newline=True
)

# Render the README file
template = env.get_template("README.md")
template.stream(organisation_name=organisation_name).dump("README.md")

# Render the README file
template = env.get_template("package.json")
template.stream(
    package_name=package_name,
    package_description=package_description,
    package_repo_url=package_repo_url,
    package_author=package_author,
).dump("package.json")

# Render the pyproject.toml file
template = env.get_template("pyproject.toml")
template.stream(
    package_name=package_name,
    package_author=package_author,
    package_description=package_description,
).dump("pyproject.toml")

# Render the .env-config.yaml file
template = env.get_template(".env-config.yaml")
template.stream(aws_account_id=aws_account_id).dump(".env-config.yaml")

# Render the tools/environments/iac.py file
template = env.get_template("tools/environments/iac.py")
template.stream(package_description=package_description).dump(
    "tools/environments/iac.py"
)

# Render the tools/environments/test.py file
template = env.get_template("tools/environments/test.py")
template.stream(aws_account_id=aws_account_id).dump("tools/environments/test.py")

# Render the terragrunt.hcl file
template = env.get_template("components/terragrunt.hcl")
template.stream(
    aws_region=aws_region,
    github_org=github_org,
    tfstate_bucket_name=tfstate_bucket_name,
).dump("components/terragrunt.hcl")
