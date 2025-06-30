# Ansible Vault Setup Guide

This playbook uses Ansible Vault to securely store sensitive information like passwords and encryption keys.

## Quick Start

### 1. Create Vault File with Template
```bash
# Generate vault password and create encrypted vault file with template
./run-ansible.py --create-vault

# Edit vault with secure credentials
./run-ansible.py --edit-vault
```

### 2. Manual Setup (Alternative)
```bash
# Generate password only
./run-ansible.py --generate-password

# Create vault manually
ansible-vault create group_vars/nas_servers/vault.yml
```

## Vault File Contents

Add the following variables to your vault file:

```yaml
---
# Ansible become password (sudo password for remote user)
vault_become_password: "your_sudo_password"

# Samba user credentials (ServerContainers format)
vault_samba_users:
  - username: "admin"
    password: "admin_secure_password_here"
    uid: "1001"
    groups: []  # Additional groups beyond default user group
  - username: "media"
    password: "media_secure_password_here"
    uid: "1002"
    groups: []

# LUKS encryption keyfiles paths
vault_luks_keyfiles:
  drive1:
    source: "luks-keys/drive1.key"
  drive2:
    source: "luks-keys/drive2.key"

# VueTorrent qBittorrent credentials
vault_vuetorrent_username: "admin"
vault_vuetorrent_password: "secure_torrent_password_here"

# NFS access credentials (if needed)
vault_nfs_allowed_networks:
  - "192.168.1.0/24"
  - "10.0.0.0/8"

# Cockpit admin credentials
vault_cockpit_admin_password: "secure_cockpit_password_here"
```

## Managing Vault Files

### View Vault Contents
```bash
ansible-vault view group_vars/nas_servers/vault.yml
```

### Edit Vault Contents
```bash
# Using the Python script (recommended)
./run-ansible.py --edit-vault

# Or manually
ansible-vault edit group_vars/nas_servers/vault.yml
```

### Change Vault Password
```bash
ansible-vault rekey group_vars/nas_servers/vault.yml
```

## Running Playbooks

### With Vault Password Prompt
```bash
./run-ansible.py -w
# Will prompt for vault password automatically
```

### With Vault Password File
The Python script automatically manages vault password files.

## LUKS Key Management

### Generate LUKS Keys
```bash
# Create LUKS keys directory
mkdir -p luks-keys
chmod 700 luks-keys

# Generate random keys for each drive
openssl rand -base64 4096 > luks-keys/drive1.key
openssl rand -base64 4096 > luks-keys/drive2.key
chmod 400 luks-keys/*.key
```

### Backup Keys Securely
- Store LUKS keys in a secure location (encrypted USB, password manager, etc.)
- Never commit keys to version control
- Consider using multiple key slots for redundancy

## Security Best Practices

1. **Never commit vault files unencrypted to version control**
2. **Use strong, unique passwords for vault encryption**
3. **Regularly rotate passwords stored in vault**
4. **Backup vault password securely**
5. **Use different vault passwords for different environments**

## Troubleshooting

### Wrong Vault Password
```bash
# Error: Decryption failed
# Solution: Check your vault password or regenerate
./run-ansible.py --generate-password
```

### Vault File Not Found
```bash
# Error: Could not find vault file
# Solution: Create one
./run-ansible.py --create-vault
```

### Permission Denied on Keys
```bash
# Error: Permission denied accessing LUKS keys
# Solution: Check file permissions (should be 400)
chmod 400 luks-keys/*.key
```
