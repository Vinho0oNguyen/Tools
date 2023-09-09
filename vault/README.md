# Vault
## 1. Vault CLI
#### Init generate unseal key
```
vault operator init -n <number_of_unseal_key> -t <number_key_correct_to_unseal> (n >= t and > 1)
```
#### Unseal key and login
```
- vault operator unseal
- vault login
```
#### Manual join to cluster
```
- vault operator raft join
- vault operator raft list-peers
```
#### Snapshot Vault Raft
```
- vault operator raft snapshot save <snapshot_file>
- vault operator raft snapshot restore <snapshot_file>
```
#### Generate access token
```
- vault write sys/auth/token/tune max_lease_ttl=90000h
- vault token create -format=json -policy="backup-policy" -period=87600h
```
## 2. Vault REST API
#### Create secret engine
```
def create_secret_engine(secret_in_vault):
    url = "https://" + vault_url + "/v1/sys/mounts/"  + secret_in_vault
    headers = {
        'X-Vault-Token': vault_token,
        'Content-Type': 'application/json'
    }
    ENGINE_CONFIG='{"type":"kv-v2"}'
    response = requests.post(url, headers=headers, data=ENGINE_CONFIG, verify=False)
```
#### Push data to Vault
```
def push_data(secret, key, content):
    url = "https://" + vault_url + "/v1/" + secret + "/data/" + key
    headers = {
        'X-Vault-Token': vault_token,
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=content, verify=False)
    
    if response.status_code >= 400:
        print("Failed to post data to Vault. Error:", response.text)
```
## 3. Install Vault into K8S with Helm (HA, HA-TLS, STANDALONE, DEV)
```
helm upgrade --install vault hashicorp/vault -f values.yaml -n vault --create-namespace
```

