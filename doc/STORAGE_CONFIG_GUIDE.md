# Storage Configuration Guide

This guide explains the centralized storage configuration system that manages all drives and their encryption, formatting, and service integration.

## Overview

The [`storage_config.yml`](storage_config.yml) file is the central configuration for all storage drives in the system. All roles (encrypt, mount, nfs-server, samba-server) use this configuration to automatically set up services based on your drive definitions.

## Configuration Structure

### LUKS Keyfiles
Define encryption keys that will be used by encrypted drives:

```yaml
luks_keyfiles:
  drive1:
    source: "luks-keys/drive1.key"
    description: "Media drive encryption key"
  drive2:
    source: "luks-keys/drive2.key" 
    description: "Backup drive encryption key"
```

### Storage Drives
Define each storage drive with comprehensive settings:

```yaml
storage_drives:
  - name: "media"                           # Unique identifier
    description: "Primary media storage"    # Human-readable description
    device: "/dev/sdb1"                     # Block device path
    mount_point: "/var/mnt/media"           # Where to mount
    fstype: "ext4"                          # Filesystem type
    
    # Encryption settings
    encrypt: true                           # Enable LUKS encryption
    luks_name: "media-encrypted"            # LUKS device name
    luks_keys:
      - key: "drive1"                       # References luks_keyfiles
        slot: 0                             # LUKS key slot (0-7)
    
    # Format settings
    format: false                           # Set to true to format (DESTRUCTIVE!)
    
    # Mount settings  
    mount_options: "defaults,noatime,nodev,nosuid"
    
    # Service integration
    nfs_export: true                        # Include in NFS exports
    samba_share: true                       # Include in Samba shares
    
    # Ownership
    owner: "root"
    group: "root"
    mode: "0755"
```

## Drive Configuration Options

### Basic Settings
- **name**: Unique identifier used throughout the system
- **description**: Human-readable description for documentation
- **device**: Full path to block device (e.g., `/dev/sdb1`)
- **mount_point**: Where the drive will be mounted (e.g., `/var/mnt/media`)
- **fstype**: Filesystem type (`ext4`, `xfs`, `btrfs`, etc.)

### Encryption Settings
- **encrypt**: `true`/`false` - Enable LUKS encryption
- **luks_name**: Name for the encrypted device (appears in `/dev/mapper/`)
- **luks_keys**: Array of key definitions
  - **key**: References entry in `luks_keyfiles`
  - **slot**: LUKS key slot number (0-7)

### Format Settings
- **format**: `true`/`false` - Whether to format the drive
  - ⚠️ **WARNING**: Setting to `true` is DESTRUCTIVE and will erase all data!

### Mount Settings
- **mount_options**: Mount options passed to the `mount` command
- **owner**: Directory owner after mounting
- **group**: Directory group after mounting  
- **mode**: Directory permissions after mounting

### Service Integration
- **nfs_export**: `true`/`false` - Include in NFS exports
- **samba_share**: `true`/`false` - Include in Samba shares

## Role Integration

### Encrypt Role
- Processes drives where `encrypt: true`
- Uses `luks_keyfiles` for encryption keys
- Validates key transfer with checksums
- Tests encrypted device mounting
- Formats drives if `format: true`

### Mount Role
- Processes all drives for mounting
- Uses encrypted devices if `encrypt: true`
- Applies `mount_options` and ownership settings
- Validates successful mounting

### NFS Server Role
- Processes drives where `nfs_export: true`
- Creates bind mounts to NFS export directory
- Configures firewall and SELinux

### Samba Server Role
- Processes drives where `samba_share: true`
- Creates container volume mounts
- Configures shares automatically

## Validation Features

### Encryption Validation
The encrypt role performs comprehensive validation:

1. **Key Transfer Validation**
   - Computes SHA256 checksums of local keyfiles
   - Transfers keys to remote host
   - Verifies remote checksums match local checksums
   - Fails if any key transfer is corrupted

2. **Post-Encryption Mount Validation**
   - Opens LUKS devices with provided keys
   - Test mounts each encrypted device
   - Creates test directory structure
   - Writes and reads test files
   - Verifies file content integrity
   - Cleans up test artifacts
   - Unmounts test mounts

### Drive Validation
All roles validate:
- Required drive properties are present
- Referenced drives exist in configuration
- Mount points are accessible
- Devices can be mounted successfully

## Usage Examples

### Basic Encrypted Drive
```yaml
- name: "documents"
  description: "Personal documents storage"
  device: "/dev/sdc1"
  mount_point: "/var/mnt/documents"
  fstype: "ext4"
  encrypt: true
  luks_name: "docs-encrypted"
  luks_keys:
    - key: "drive3"
      slot: 0
  format: false
  mount_options: "defaults,noatime,nodev,nosuid"
  nfs_export: false
  samba_share: true
  owner: "root"
  group: "root"
  mode: "0755"
```

### Unencrypted Temporary Drive
```yaml
- name: "temp"
  description: "Temporary storage (no encryption)"
  device: "/dev/sdd1"
  mount_point: "/var/mnt/temp"
  fstype: "ext4"
  encrypt: false
  format: false
  mount_options: "defaults,noatime,nodev,nosuid,noexec"
  nfs_export: false
  samba_share: false
  owner: "root"
  group: "root"
  mode: "0755"
```

### Time Machine Backup Drive
```yaml
- name: "timemachine"
  description: "macOS Time Machine backups"
  device: "/dev/sde1"
  mount_point: "/var/mnt/timemachine"
  fstype: "ext4"
  encrypt: true
  luks_name: "tm-encrypted"
  luks_keys:
    - key: "backup_key"
      slot: 0
  format: false
  mount_options: "defaults,noatime"
  nfs_export: false
  samba_share: true
  owner: "root"
  group: "root"
  mode: "0755"
```

## Security Best Practices

1. **Always use encryption** for sensitive data
2. **Never set format: true** unless you want to destroy data
3. **Use strong keyfiles** generated with `openssl rand -base64 4096`
4. **Store keyfiles securely** and back them up safely
5. **Use restrictive mount options** like `nodev,nosuid,noexec` when appropriate
6. **Test thoroughly** in a development environment first

## Troubleshooting

### Key Transfer Failures
If checksum validation fails:
1. Check local keyfile exists and is readable
2. Verify network connectivity to target host
3. Ensure sufficient disk space on target
4. Check file permissions on source keyfile

### Mount Failures
If post-encryption validation fails:
1. Verify LUKS device opened successfully
2. Check filesystem type matches device
3. Ensure mount point directory exists
4. Verify sufficient permissions for test operations

### Service Integration Issues
If NFS/Samba services don't see drives:
1. Ensure `nfs_export`/`samba_share` is set to `true`
2. Check drive is successfully mounted
3. Verify service-specific configuration is correct
4. Check firewall and SELinux settings
