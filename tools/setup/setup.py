#!/usr/bin/env python3
from jinja2 import Environment
from jinja2 import FileSystemLoader

package_name = input("Enter your package name (e.g. acme-limited-iac-project): ")
package_description = input("Enter your package description: ")
package_repo_url = input(
    "Enter your GitHub repository URL (e.g. git@github.com:acme-limited/iac.git): "
)
github_org = input("Enter your GitHub Organisation: ")
package_author = input("Enter your full name (e.g. Joe Smith): ")
aws_region = input("Enter your AWS region (e.g. eu-west-2): ")
tfstate_bucket_name = input(
    "Enter your Terraform State S3 bucket name prefix: (e.g. acme-limited-tfstate):"
)
organisation_name = input("Enter your company's name: Acme Limited")

env = Environment(loader=FileSystemLoader("."))

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

# Render the terragrunt.hcl file
template = env.get_template("components/terragrunt.hcl")
template.stream(
    aws_region=aws_region,
    github_org=github_org,
    tfstate_bucket_name=tfstate_bucket_name,
).dump("components/terragrunt.hcl")
