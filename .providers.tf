terraform {
  required_version = "= 0.14.8"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
    archive = {
      source = "hashicorp/archive"
      version = "~> 2.1"
    }
  }
}

provider aws {
  region  = "eu-west-2"
}
