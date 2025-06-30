# NAS Server Ansible Playbook

An enterprise-grade Ansible playbook for deploying and managing NAS servers on Fedora CoreOS with containerized services.

## Features

🔐 **Security-First Design**
- SMB3.11-only with mandatory signing and encryption
- Ansible Vault integration for secrets management
- LUKS disk encryption support
- Multi-user Samba configuration

🚀 **Immutable OS Ready**
- Designed for Fedora CoreOS/IoT
- Containerized services via Quadlet
- rpm-ostree package layering

🛠️ **Service Stack**
- **Samba**: Enterprise SMB server with Avahi/WSDD2 discovery (ServerContainers)
- **NFS**: Network File System exports with verification
- **VueTorrent**: Modern qBittorrent web UI with torrent management
- **LUKS**: Full disk encryption with key management
- **Cockpit**: Web-based system management

## Quick Start

### 1. Prerequisites
```bash
# Install Ansible and required collections
pip install ansible
ansible-galaxy install -r requirements.yml
```

### 2. Setup Vault (First Time)
```bash
# Generate vault password and create encrypted vault file with template
./run-ansible.py --create-vault

# Or generate password only
./run-ansible.py --generate-password

# Edit vault with secure credentials
./run-ansible.py --edit-vault

# See VAULT_SETUP.md for detailed vault configuration
```

### 3. Configure Your Storage
Edit `storage_config.yml` to define your drives:
- Storage devices and mount points
- Encryption settings (LUKS)
- Service integration (NFS/Samba)
- Format options

The system auto-generates service configurations from this central file.

### 4. Deploy

```bash
# Dry run (recommended first)
./run-ansible.py

# Apply changes
./run-ansible.py -w

# Target specific host
./run-ansible.py --host nas-server -w

# Verbose output
./run-ansible.py -v 3 -w
```

## Python Runner Script

The included `run-ansible.py` script simplifies operations:

### Basic Usage
```bash
./run-ansible.py                      # Dry run (check mode)
./run-ansible.py -w                   # Apply changes
./run-ansible.py -s                   # Syntax check only
./run-ansible.py -p samba-server.yml  # Deploy Samba only
./run-ansible.py -p vuetorrent.yml    # Deploy VueTorrent only
```

### Advanced Options
```bash
./run-ansible.py -v 2 -w            # Verbose level 2 + apply
./run-ansible.py -p nfs-server.yml  # Custom playbook
./run-ansible.py --host nas-01 -w   # Target specific host
./run-ansible.py --generate-password # Generate new vault password
```

### Features
- **Safe by default**: Runs in check mode unless `-w` specified
- **Auto vault management**: Generates secure passwords automatically
- **Structure validation**: Verifies Ansible directory structure
- **Flexible targeting**: Support for custom playbooks and hosts

## Directory Structure

```
├── run-ansible.py              # Simplified runner script
├── site.yml                    # Main playbook
├── ansible.cfg                 # Ansible configuration
├── inventory/hosts.ini          # Host definitions
├── group_vars/
│   └── nas_servers/
│       ├── vars.yml            # Public variables
│       └── vault.yml           # Encrypted secrets
├── roles/
│   ├── samba-server/           # SMB shares
│   ├── nfs-server/             # NFS exports
│   ├── vuetorrent/             # qBittorrent with VueTorrent UI
│   ├── encrypt/                # LUKS encryption
│   └── mount/                  # Storage mounting
└── luks-keys/                  # Encryption keys (create manually)
```

## Configuration Examples

### Samba User Setup (ServerContainers)
```yaml
# In vault.yml (encrypted)
vault_samba_users:
  - username: "admin"
    password: "admin_secure_password"
    uid: "1001"
    groups: []  # Additional groups
  - username: "media"
    password: "media_secure_password"
    uid: "1002"
    groups: []
```

### Storage Configuration (Centralized)
```yaml
# In storage_config.yml - Central configuration for all drives
storage_drives:
  - name: "media"
    description: "Primary media storage"
    device: "/dev/sdb1"
    mount_point: "/var/mnt/media"
    fstype: "ext4"
    
    # Encryption settings
    encrypt: true
    luks_name: "media-encrypted" 
    luks_keys:
      - key: "drive1"
        slot: 0
    
    # Format settings (DESTRUCTIVE!)
    format: false
    
    # Mount settings
    mount_options: "defaults,noatime,nodev,nosuid"
    
    # Service integration
    nfs_export: true      # Include in NFS
    samba_share: true     # Include in Samba
    
    # Ownership
    owner: "root"
    group: "root"
    mode: "0755"
```

## Security Features

### Samba Features (ServerContainers)
- SMB3.11 protocol only (no legacy SMB1/2)
- Mandatory signing and encryption
- Avahi/Bonjour discovery for macOS
- WSDD2 for Windows network discovery
- Time Machine support
- Multi-user authentication
- Performance optimizations

### LUKS Encryption
- Full disk encryption for sensitive data
- Secure key management via vault
- Multiple key slot support
- Automated unlocking

### Access Control
- Multi-user authentication
- Vault-encrypted passwords
- Sudo authentication via vault
- Firewall integration

## Verification & Testing

The playbook includes built-in verification:

### NFS Testing
- Port availability checks
- Export listing verification  
- Mount/write/unmount tests

### Samba Testing
- Service health checks
- Container status validation
- Configuration syntax verification

### LUKS Testing
- Keyfile integrity verification
- Device unlock testing
- Mount point validation

## Troubleshooting

### Common Issues

**Vault Password Error**
```bash
# Check vault password file
cat .vault_pass

# Regenerate if needed
./run-ansible.py --generate-password
```

**Permission Denied on LUKS Keys**
```bash
# Fix key permissions
chmod 400 luks-keys/*.key
```

**Service Start Failures**
```bash
# Check systemd status
systemctl status samba.service
systemctl status nfs-server.service

# View logs
journalctl -u samba.service -f
```

## Documentation

- [`STORAGE_CONFIG_GUIDE.md`](STORAGE_CONFIG_GUIDE.md) - Centralized storage configuration and validation
- [`VAULT_SETUP.md`](VAULT_SETUP.md) - Comprehensive vault management guide
- [`AGENT.md`](AGENT.md) - Command reference and conventions

## License

MIT License - see LICENSE file for details.
