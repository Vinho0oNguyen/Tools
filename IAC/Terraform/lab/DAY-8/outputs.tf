output "data-center-id" {
    value = data.vsphere_datacenter.datacenter.id
}

output "data-center-name" {
    value = data.vsphere_datacenter.datacenter.name
}

output "data-template" {
    value = data.vsphere_virtual_machine.vm.name
}

output "id-server" {
    value = vsphere_virtual_machine.lab-vm[*].id
}

output "name-server" {
    value = vsphere_virtual_machine.lab-vm[*].name
}

output "ipv4-server" {
    value = vsphere_virtual_machine.lab-vm[*].default_ip_address
}

output "host" {
    value = data.vsphere_host.host[*].name
}