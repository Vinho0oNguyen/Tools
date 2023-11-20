terraform {
    cloud {
        organization = "lab-01"
        workspaces {
        name = "demo"
        }
    }
    
    required_providers {
        vsphere = {
        source = "hashicorp/vsphere"
        version = "2.5.1"
        }
    }

    # backend "s3" {
    #     bucket = "terraform-stats01"
    #     key = "dev/vcenter-inti-server-k8s/terraform.tfstate"
    #     access_key = var.access_key_s3
    #     secret_key = var.secret_s3
    #     region = var.region_s3

    #     # Enable during State Locking
    #     dynamodb_table = "dev-day8-init-server-k8s"
    # }
}

provider "aws" {
    access_key = var.access_key_s3
    secret_key = var.secret_s3
    region = var.region_s3
}

provider "vsphere" {
    user                 = var.vsphere_user
    password             = var.vsphere_password
    vsphere_server       = var.vsphere_server
    allow_unverified_ssl = true
}