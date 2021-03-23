terraform {
  source = "../../../modules//_bootstrap_resource_groups"
}

include {
  path = find_in_parent_folders()
}

locals {
  global_vars    = read_terragrunt_config(find_in_parent_folders("terragrunt.hcl"))
  bootstrap_vars = read_terragrunt_config(find_in_parent_folders("bootstrap.hcl"))
  tags = merge(
    local.global_vars.inputs.tags,
    local.bootstrap_vars.inputs.tags,
    {
      component = "bootstrap/resource_groups"
    }
  )
}

inputs = {
  tags = local.tags
}
