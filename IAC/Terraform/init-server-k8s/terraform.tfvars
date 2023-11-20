vsphere_user = "administrator@vsphere.local"
vsphere_password = "P@&&vv0rd:@@Admin"
vsphere_server = "vcenter-hni.fbox.fpt.vn"

prefix_name = "vinhntq-lab-terraform"

datastore-hdd = "HDD-184"

host = ["fpl-esxi-184.fbox.fpt.vn", "fpl-esxi-185.fbox.fpt.vn", "fpl-esxi-186.fbox.fpt.vn"]
template = "420efd26-8c96-fa08-81d5-2dafc7bbd984"

network = "Vlan2002-LocalFW"
name_server = {
    "master-01" = "172.24.246.239"
    "master-02" = "172.24.246.240"
    "worker-01" = "172.24.246.241"
    "worker-02" = "172.24.246.242"
}
ipv4_gateway = "172.24.246.129"

resource_master = {
    "cpu" = 3
    "memory" = 3072
    "disk" = 100
}

resource_worker = {
    "cpu" = 2
    "memory" = 2048
    "disk" = 200
} 

cpu_hot_add_enabled = true
memory_hot_add_enabled = true

