# Bootstrap -> ResourceGroups Root Module

[![stable](http://badges.github.io/stability-badges/dist/stable.svg)](http://github.com/badges/stability-badges)

Adds resource groups that filter on tags

<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| aws | n/a |

## Modules

No Modules.

## Resources

| Name |
|------|
| [aws_resourcegroups_group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/resourcegroups_group) |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| environment | The environment in which to deploy (e.g. root, staging or production) | `string` | n/a | yes |
| resource\_groups | This list is all the resources groups set at component\_root level | `set(string)` | <pre>[<br>  "bootstrap"<br>]</pre> | no |
| tags | Tags to apply to all resources in this module | `map(string)` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| resource\_group\_count | n/a |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
