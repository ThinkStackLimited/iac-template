# Infrastructure as Code (iac)

Implements the development, testing and maintenance of {{organisation_name}}'s infrastructure.

<!-- toc -->

- [Requirements](#requirements)
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

## Setup

```shell script
make setup
```

## Testing

To test the python code that controls the order of deploying Terragrunt components, run the following:

```shell script
make test
```

## Initialise new environment

```shell script
# Plan terraform run
make bootstrap_plan
# Apply terraform run
make bootstrap_apply
```

## Deployment

```shell script
# Plan terraform run
make plan
# Apply terraform run
make apply
```

## References
