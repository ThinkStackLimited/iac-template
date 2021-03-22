locals {
  aws_region         = "{{aws_region}}"
  environment        = get_env("TG_ENV", "")
  environments       = get_env("TG_ENVS", "{}")
  github_org         = "{{github_org}}"
  terraform_version  = file("../.terraform-version")
  terragrunt_version = file("../.terragrunt-version")
  tfstate_bucket     = "{{tfstate_bucket_name}}-tfstate-${local.environment}-${get_aws_account_id()}"
  tfstate_key        = "${path_relative_to_include()}/terraform.tfstate"

  tags = {
    environment        = local.environment
    terragrunt_version = trimspace("v${local.terragrunt_version}")
    terraform_version  = trimspace("v${local.terraform_version}")
  }
}

remote_state {
  backend = "s3"
  config = {
    bucket         = local.tfstate_bucket
    dynamodb_table = "terraform_state_locks"
    encrypt        = true
    key            = local.tfstate_key
    region         = local.aws_region
  }
  generate = {
    path      = "remote_state.tf"
    if_exists = "overwrite"
  }
}

generate provider {
  path      = "temp_providers.tf"
  if_exists = "overwrite"
  contents  = file("../.providers.tf")
}

inputs = {
  aws_region                   = local.aws_region
  blog_build_agent             = local.blog_build_agent
  environment                  = local.environment
  environments                 = local.environments
  github_org                   = local.github_org
  iac_build_agent              = local.iac_build_agent
  terraform_version            = local.terraform_version
  terragrunt_version           = local.terragrunt_version
  tfstate_global_bucket        = local.tfstate_bucket
  tfstate_global_bucket_region = local.aws_region
  tags                         = local.tags
}

# Customise terraform
terraform {
  extra_arguments disable_input {
    commands  = get_terraform_commands_that_need_input()
    arguments = ["-input=false"]
  }
}
