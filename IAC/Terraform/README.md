# Init server vcenter for k8s

## Variables required
vsphere_user

vsphere_password

vsphere_server

prefix_name

datastore-hdd

host

template

network

name_server = {
    "master-01" = "x.x.x.x"
    "master-02" = "x.x.x.x"
    "worker-01" = "x.x.x.x"
    "worker-02" = "x.x.x.x"
}

ipv4_gateway = "x.x.x.x"


## Variables options

resource_master = {
    "cpu" = x
    "memory" = x
    "disk" = x
}

resource_worker = {
    "cpu" = x
    "memory" = x
    "disk" = x
} 

cpu_hot_add_enabled (bool; default: true)

memory_hot_add_enabled (bool; default: true)


