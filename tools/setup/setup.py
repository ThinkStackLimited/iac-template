#!/usr/bin/env python3
from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import Template

package_name = input("Enter your package name: ")
package_description = input("Enter your package description: ")
package_repo_url = input("Enter your GitHub repository URL: ")
github_org = input("Enter your GitHub Organisation: ")
package_author = input("Enter your full name: ")
aws_region = input("Enter your AWS region: ")
tfstate_bucket_name = input("Enter your Terraform State S3 bucket name: ")
organisation_name = input("Enter your company's name: ")

# Render the README file


# env = Environment(loader=FileSystemLoader('templates'))
# template = env.get_template('test.html')
#
#
# Template('Hello {{ name }}!').stream(name='foo').dump('hello.html')
