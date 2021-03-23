# Infrastructure as Code (iac)

Implements the development, testing and maintenance of {{organisation_name}}'s infrastructure.

<!-- toc -->

- [Requirements](#requirements)
- [Run Template Update](#run-template-update)
- [Setup](#setup)
- [Testing](#testing)
- [Initialise new environment](#initialise-new-environment)
- [Deployment](#deployment)
- [References](#references)

<!-- tocstop -->

## Requirements

* [Terragrunt](https://github.com/gruntwork-io/terragrunt#install-terragrunt) is used to manage environments and
prevent repetitive code.
* [Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli?in=terraform/aws-get-started) is used to
manage the AWS resources.
* [Python v3](https://www.python.org/downloads/) will co-ordinate the deployment of resources via Terragrunt.
* [Poetry](https://python-poetry.org/docs/) will be used to manage the Python build environment.

## Run Template Update

This command will take input and run Jinja template updates against certain files to seed the repo with organisation
specific details e.g. Organisation name, GitHub repo etc.

```shell
make template
```

## Setup

Once the template updates have been performed, run this command to set up your local environment.

```shell
make setup
```

## Testing

To test the python code that controls the order of deploying Terragrunt components, run the following:

```shell
make test
```

## Initialise new environment

```shell
# Plan terraform run
make bootstrap_plan
# Apply terraform run
make bootstrap_apply
```

## Deployment

```shell
# Plan terraform run
make plan
# Apply terraform run
make apply
```

## References
