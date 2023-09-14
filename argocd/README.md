# ARGOCD
## ADD NEW USER AND CLI
### Get init user admin
#### CLI
```
argocd admin initial-password -n argocd
```
#### Get from secret K8S
Get from secret argocd-initial-admin-secret in namespace argocd
```
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath='{.data.password}'|base64 --decode
```
### ADD NEW USER
#### Config file argocd-cm
```
apiVersion: v1
data:
  accounts.teamsmarttv: apiKey,login
  accounts.teamweb: apiKey,login
  accounts.usersync: apiKey,login
  account.example: apiKey,login
  admin.enabled: 'true'
  application.instanceLabelKey: argocd.argoproj.io/instance
  exec.enabled: 'true'
  server.rbac.log.enforce.enable: 'false'
  timeout.hard.reconciliation: 0s
  timeout.reconciliation: 3s
kind: ConfigMap
```
#### Update password for new user
1. Manage user list:
```
argocd account list
```
2. Set password for user
```
argocd account update-password \
  --account <name> \
  --current-password <admin_password> \
  --new-password <admin_password>
```
#### Phân quyền user login Argocd
Change config file argocd-rbac:
```
apiVersion: v1
data:
  policy.csv: >-
    p, role:sync, projects, get, *, allow 
    p, role:sync, applications, get, */*, allow 
    p, role:sync, logs, get, */*, allow 
    p, role:sync, applications, sync, */*, allow
    p, role:backend, applications, get, *api/*, allow 
    p, role:backend, exec, create, *api/*, allow 
    p, role:backend, logs, get, *api/*, allow
    p, role:backend, applications, sync, *api/*, allow
    p, role:backend, applications, action/apps/Deployment/restart, *api/*, allow
    p, role:cms, applications, get, *-cms/*, allow 
    p, role:cms, exec, create, *-cms/*, allow 
    p, role:cms, logs, get,*-cms/*, allow
    p, role:web, applications, get, *-web/*, allow 
    p, role:web, exec, create, *-web/*, allow 
    p, role:web, logs, get,*-web/*, allow
    p, role:smarttv, applications, get, *-smarttv/*, allow 
    p, role:smarttv, exec, create, *-smarttv/*, allow 
    p, role:smarttv, logs, get, *-smarttv/*, allow
    p, role:ads, applications, get, ads/*, allow 
    p, role:ads, exec, create, ads/*, allow 
    p, role:ads, logs, get, ads/*, allow
    p, role:ads, applications, action/apps/Deployment/restart, ads/*, allow
    p, role:gameshow, applications, get, *-gameshow/*, allow 
    p, role:gameshow, exec, create, *-gameshow/*, allow 
    p, role:gameshow, logs, get, *-gameshow/*, allow
    p, role:bigdata, applications, get, bigdata/*, allow 
    p, role:bigdata, exec, create, bigdata/*, allow 
    p, role:bigdata, logs, get, bigdata/*, allow
    p, role:bigdata, applications, get, iptv-api/izios-*, allow 
    p, role:bigdata, exec, create, iptv-api/izios-*, allow 
    p, role:bigdata, logs, get, iptv-api/izios-*, allow
    p, role:smarthome, applications, get, smarthome/*, allow 
    p, role:smarthome, exec, create, smarthome/*, allow 
    p, role:smarthome, logs, get, smarthome/*, allow
    p, role:payment, applications, get, *-payment/*, allow 
    p, role:payment, exec, create, *-payment/*, allow 
    p, role:payment, logs, get, *-payment/*, allow
    p, role:payment, applications, action/apps/Deployment/restart, *-payment/*,
    allow
    g, usersync, role:sync 
    g, teambackend, role:backend
    g, teamcms, role:cms
    g, teamweb, role:web 
    g, teamsmarttv, role:smarttv 
    g, teamads, role:ads 
    g, teamgameshow, role:gameshow 
    g, teambigdata, role:bigdata       
    g, teamsmarthome, role:smarthome 
    g, teampayment, role:payment
    g, api-payment, role:payment
    g, api-payment, role:backend
  policy.default: ''
  scopes: '[groups]'
kind: ConfigMap
```
#### Allow exec to pod

## Install
#### NON-HA
```
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.8.3/manifests/install.yaml
```
#### HA
```
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.8.3/manifests/ha/install.yaml
```
### ARGOCD IMAGE UPDATER
```
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj-labs/argocd-image-updater/stable/manifests/install.yaml
```
> **_NOTE:_**  Thêm config để interval check repo: **--interval 10** trong deployment: **spec.template.spec.containers.command**.
## Manifest Structure
### Applications folder
#### Chứa resource Application của argocd dùng để quản lý và triển khai app.
Manifest File:
```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  labels:
    type: deployment
  annotations:
    argocd-image-updater.argoproj.io/git-branch: ott-prod
    argocd-image-updater.argoproj.io/image-list: myimage=docker-registry.fbox.fpt.vn/api/api-main
    argocd-image-updater.argoproj.io/myalias.force-update: "true"
    argocd-image-updater.argoproj.io/myimage.allow-tags: regexp:^master-build-.*$
    argocd-image-updater.argoproj.io/myimage.pull-secret: secret:argo-cd/harbor-ott#credential
    argocd-image-updater.argoproj.io/myimage.update-strategy: latest
    argocd-image-updater.argoproj.io/write-back-method: 'git:secret:argo-cd/git-creds'
    argocd-image-updater.argoproj.io/myimage.helm.image-name: deployment.repository
    argocd-image-updater.argoproj.io/myimage.helm.image-tag: deployment.tag
    notifications.argoproj.io/subscribe.out-of-sync.telegram: "-987170400"
    notifications.argoproj.io/subscribe.on-sync-succeeded.telegram: "-987170400"
  name: api-fptplay-api-prod-fpl
spec:
  destination:
    namespace: api
    server: https://kubernetes.default.svc
  project: api
  source:
    helm:
      valueFiles:
      - values/api/fptplay-api/deployment.yaml
      - values/api/fptplay-api/healthcheck.yaml
      - values/api/fptplay-api/ingress.yaml
      - values/api/fptplay-api/cronjob.yaml
      - values/api/fptplay-api/secret.yaml
      - values/api/fptplay-api/volumes.yaml
    path: manifest
    repoURL: https://git.fpt.net/fpl/he-thong/devops/cicd-template.git
    targetRevision: ott-prod
  syncPolicy:
    syncOptions:
    - PruneLast=true
    - CreateNamespace=true

```
#### Tạo secret để xác thực với git
```
kubectl -n argocd create secret generic git-creds \
  --from-literal=username=vinho0onguyen --from-literal=password=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
```
#### Tạo xác thực registry trong K8S
### Manifest folder
#### Teamplate folder
Teamplate viết theo format helm
#### Value folder
Values cho Teamplate

