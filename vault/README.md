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
- vault operator raft join <http://ip:port>
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
#### Walk to create a list of secret into Vault
```
def walk():
    completed_files = 0

    secret_in_vault = get_secret(path)
    for i in secret_in_vault:
        create_secret_engine(i)
        full_path = path + "\\" + i
        file_names = os.listdir(full_path)
        for key in  file_names:
            if ".snap" in key:
                continue
            content = get_data(full_path + "\\" + key)
            try:
                content = json.dumps(eval(content))
                result = "{\"data\":" + " " + content + "}"
                push_data(i, key, result)
            except Exception as e:
                print(f'Error: {str(e)}')
            completed_files += 1
            pbar.update(min(total_file, completed_files))
```
## 3. Install Vault into K8S with Helm (HA, HA-TLS, STANDALONE, DEV)
```
helm upgrade --install vault hashicorp/vault -f values.yaml -n vault --create-namespace
```
## 4. Generate TLS
```
cfssl gencert -initca ca-csr.json | cfssljson -bare ca
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=vault-hni vault-csr.json | cfssljson -bare vault
```
Copy vault-key.pem  vault.csr  vault.pem to secret k8s ns vault

