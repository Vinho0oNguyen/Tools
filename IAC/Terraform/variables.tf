###########
# LOCALS ##
###########
locals {
    prefix_name = "[${var.prefix_name}]"
}

###################### 
# VARIABLES VCENTER ##
######################
variable "vsphere_user" {
    type = string
    description = "User name"
}
variable "vsphere_password" {
    type = string
    description = "Password"
}
variable "vsphere_server" {
    type = string
    description = "Server vcentert"
}


########################
# VARIABLES DATASTORE ##
########################
variable "datastore-hdd" {}


########################
# VARIABLES NETWORK ##
########################
variable "network" {}
variable "name_server" {
    type = map(string)
}
variable "ipv4_gateway" {
    type = string
}


#########################################
# VARIBALES HOST DEPLOYED AND TEMPLATE ##
#########################################
variable "host" {}
variable "template" {}


###############################
# VARIABLES RESOURCE SERVER ###
###############################
variable "prefix_name" {
    type = string
}

variable "resource_master" {
    type = map(number)
    default = {
        "cpu" = 1
        "memory" = 1024
        "disk" = 100
    }
}
variable "resource_worker" {
    type = map(number)
    default = {
        "cpu" = 1
        "memory" = 1024
        "disk" = 100
    }
}
variable "cpu_hot_add_enabled" {
    type = bool
    default = true
}
variable "memory_hot_add_enabled" {
    type = bool
    default = true
}
