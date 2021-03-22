variable "environment" {
  description = "The environment in which to deploy (e.g. root, staging or production)"
  type        = string
}

variable "resource_groups" {
  description = "This list is all the resources groups set at component_root level"
  type        = set(string)
  default     = ["bootstrap"]
}

variable "tags" {
  description = "Tags to apply to all resources in this module"
  type        = map(string)
}
