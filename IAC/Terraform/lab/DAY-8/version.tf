terraform {
    required_providers {
        vsphere = {
        source = "hashicorp/vsphere"
        version = "2.5.1"
        }
    }

    backend "s3" {
        bucket = "terraform-stats01"
        key = "dev/vcenter-inti-server-k8s/terraform.tfstate"
        access_key = "AKIA2FK22L3P3EHLOZHK"
        secret_key = "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"
        region = "ap-southeast-1"

        # Enable during State Locking
        dynamodb_table = "dev-day8-init-server-k8s"
    }
}

provider "aws" {
  region = "ap-southeast-1"
  access_key = "AKIA2FK22L3P3EHLOZHK"
  secret_key = "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"
}

provider "vsphere" {
    user                 = var.vsphere_user
    password             = var.vsphere_password
    vsphere_server       = var.vsphere_server
    allow_unverified_ssl = true
}