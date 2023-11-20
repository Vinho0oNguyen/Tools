###############
# DATA ########
###############
data "vsphere_datacenter" "datacenter" {}

data "vsphere_datastore" "HDD" {
  name          = var.datastore-hdd
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

data "vsphere_host" "host" {
    count = length(var.host)
    datacenter_id = data.vsphere_datacenter.datacenter.id
    name = var.host[count.index]
}

data "vsphere_virtual_machine" "vm" {
    uuid = var.template
    datacenter_id = data.vsphere_datacenter.datacenter.id
}

data "vsphere_network" "network" {
    name          = var.network
    datacenter_id = data.vsphere_datacenter.datacenter.id
}


##################
# RESOURCES ######
##################
resource "vsphere_virtual_machine" "lab-vm" {
    count = length(keys(var.name_server))

    name             = upper("${local.prefix_name}_${keys(var.name_server)[count.index]}-${regex("[0-9]+\\.[0-9]+\\.([0-9]+\\.[0-9]+)", var.name_server[keys(var.name_server)[count.index]])[0]}")

    resource_pool_id = data.vsphere_host.host[count.index%length(data.vsphere_host.host)].resource_pool_id
    datastore_id     = data.vsphere_datastore.HDD.id

    num_cpus         = can(regex("master.*", keys(var.name_server)[count.index])) ? var.resource_master["cpu"] : var.resource_worker["cpu"]
    cpu_hot_add_enabled = var.cpu_hot_add_enabled

    memory           = can(regex("master.*", keys(var.name_server)[count.index])) ? var.resource_master["memory"] : var.resource_worker["memory"]
    memory_hot_add_enabled = var.memory_hot_add_enabled
    
    guest_id = data.vsphere_virtual_machine.vm.guest_id
    scsi_type = data.vsphere_virtual_machine.vm.scsi_type

    network_interface {
        network_id = data.vsphere_network.network.id
    }

    disk {
        label = "${keys(var.name_server)[count.index]}"
        size  = can(regex("master.*", keys(var.name_server)[count.index])) ? var.resource_master["disk"] : var.resource_worker["disk"]
    }

    clone {
        template_uuid = data.vsphere_virtual_machine.vm.uuid
        customize {
            linux_options {
                host_name = "${keys(var.name_server)[count.index]}"
                domain = "${keys(var.name_server)[count.index]}.fptplay.net"
            }
            network_interface {
                ipv4_address = "${var.name_server[keys(var.name_server)[count.index]]}"
                ipv4_netmask = 25
            }
            ipv4_gateway = var.ipv4_gateway
        }
    }
    
}