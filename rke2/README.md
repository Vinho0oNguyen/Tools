# INSTALL K8S WITH RKE2 HA AND IPVS
## About file when install rke2
1. Folder have config: **/etc/rancher/rke2/**
2. Kubeconfig: **/etc/rancher/rke2/rke2.yaml**
3. CLI containerd: **/var/lib/rancher/rke2/bin/***
4. Folder data: **/var/lib/rancher/rke2/*** (data db, tls, token server/agent,...)
5. Folder manifest helm install addon: **/var/lib/rancher/rke2/server/manifests/***
6. File token to agent connect to servver (exist in server node): **/var/lib/rancher/rke2/server/node-token**
    > **_NOTE:_**
    https://docs.rke2.io/install/quickstart

## INSTALL AND CONFIG RKE2 SERVER
### Prerequire
\- Have **containerd**
> **_NOTE:_**
Can install docker to auto install containerd or install manual in link: https://slateci.io/docs/cluster/manual/containerd.html\

\- Install ipvsadm tools
> yum install ipset ipvsadm -y

\- add proxy
```
mkdir -p /etc/sysconfig
vim /etc/sysconfig/rke2-server
pass:
    HTTP_PROXY=proxy.hcm.fpt.vn:80
    HTTPS_PROXY=proxy.hcm.fpt.vn:80
    NO_PROXY="127.0.0.1,localhost,172.0.0.0/8,10.0.0.0/8,git.fpt.net,.fptplay.net,rancher-staging.fptplay.net"
```
### Config
#### Install rke2 tools with spec version
- curl https://get.rke2.io | INSTALL_RKE2_VERSION=**v1.28.2+rke2r1** sh -
    > **_NOTE:_**
    rke2 release: https://github.com/rancher/rke2/releases

#### Config helmchart calico for rke2 server
- mkdir -p /var/lib/rancher/rke2/server/manifests
- vim rke2-calico-config.yaml
    ```
    apiVersion: helm.cattle.io/v1
    kind: HelmChartConfig
    metadata:
      name: rke2-calico
      namespace: kube-system
    spec:
      valuesContent: |-
        installation:
          calicoNetwork:
            mtu: 9000
    ```
#### Config file config.yaml for rke2 server
- Create folder have **config.yaml**.
- Lauch first server nodes
    ```
    token: <my-shared-secret>
    kube-proxy-arg:
      - proxy-mode=ipvs
      - ipvs-strict-arp=true
    node-taint:
    - "CriticalAddonsOnly=true:NoExecute"
    ```
- Lauch addition server nodes
    ```
    kube-proxy-arg:
      - proxy-mode=ipvs
      - ipvs-strict-arp=true
    server: https://<ip first server node>
    token: <my-shared-secret>
    node-taint:
    - "CriticalAddonsOnly=true:NoExecute"
    ```
    > **_NOTE:_**
    https://docs.rke2.io/install/ha
    
- Lauch with external etcd
Can install rke like config above with additions:
    ```
    Disable all config about contolplane in node deploy etcd
        disable-apiserver: true
        disable-controller-manager: true
        disable-kube-proxy: false
        disable-scheduler: true
    Disable deploy etcd in another controleplane
        disable-etcd: true
        disable-kube-proxy: false
        etcd-expose-metrics: false
    ```
    > **_NOTE:_**
    https://www.suse.com/support/kb/doc/?id=000020771

- Config systemd for rke2 server
    ```
    [Unit]
    Description=Rancher Kubernetes Engine v2 (server)
    Documentation=https://github.com/rancher/rke2#readme
    Wants=network-online.target
    After=network-online.target
    Conflicts=rke2-agent.service
    
    [Install]
    WantedBy=multi-user.target
    
    [Service]
    Type=notify
    EnvironmentFile=-/etc/sysconfig/rke2-server
    KillMode=process
    Delegate=yes
    LimitNOFILE=1048576
    LimitNPROC=infinity
    LimitCORE=infinity
    TasksMax=infinity
    TimeoutStartSec=0
    Restart=always
    RestartSec=5s
    ExecStartPre=-/sbin/modprobe br_netfilter
    ExecStartPre=-/sbin/modprobe overlay
    ExecStart=/usr/local/bin/rke2 server --cni calico --config /etc/rancher/rke2/config.yaml
    ExecStopPost=-/bin/sh -c "systemd-cgls /system.slice/%n | grep -Eo '[0-9]+ (containerd|kubelet)' | awk '{print $1}' | xargs -r kill"
    ```
## INSTALL AND CONFIG RKE2 AGENT
