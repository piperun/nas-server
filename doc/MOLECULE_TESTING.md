# Molecule Testing Guide

## Overview

This project uses [Ansible Molecule](https://molecule.readthedocs.io/) for testing containerized services in isolated environments. Molecule provides safe, automated testing without affecting your production systems.

## What Gets Tested

### ✅ Tested Services (Containerized)
- **Samba Server** - SMB/CIFS file sharing with ServerContainers
- **NFS Server** - Network File System exports  
- **VueTorrent** - qBittorrent with Vue.js WebUI
- **Cockpit** - Web-based system administration

### ⚠️ Skipped Components (Hardware-Dependent)
- **Encrypt Role** - Requires real block devices and LUKS
- **Mount Role** - Requires real filesystems and storage

## Installation

### Prerequisites
```bash
# Install Python requirements
pip install -r requirements.txt

# Or install Molecule manually  
pip install molecule[podman]

# Verify installation
molecule --version
```

### Configuration Notes
The Molecule scenarios use `ANSIBLE_ROLES_PATH` environment variable to locate roles in the `../../roles` directory relative to each scenario. This ensures Molecule can find the project roles without complex path configurations.

### System Requirements
- **Podman** - Container runtime (preferred over Docker)
- **Python 3.8+** - For Molecule
- **Ansible 8.0+** - Automation platform

## Test Scenarios

### Available Test Scenarios

| Scenario | Description | Services Tested |
|----------|-------------|-----------------|
| `default` | Full integration test | All containerized services |
| `samba` | Samba-only testing | SMB/CIFS file sharing |
| `nfs` | NFS-only testing | Network file exports |
| `vuetorrent` | VueTorrent-only testing | qBittorrent WebUI |
| `cockpit` | Cockpit-only testing | Web administration |

## Usage

### Using run-ansible.py (Recommended)

```bash
# Run all tests (default scenario)
./run-ansible.py test

# Test specific service
./run-ansible.py test --scenario samba
./run-ansible.py test --scenario nfs
./run-ansible.py test --scenario vuetorrent  
./run-ansible.py test --scenario cockpit

# Run with verbose output
./run-ansible.py test --scenario samba -v 2
```

### Direct Molecule Commands

```bash
# List available scenarios
molecule list

# Run default scenario
molecule test

# Run specific scenario
molecule test -s samba
molecule test -s nfs
molecule test -s vuetorrent
molecule test -s cockpit

# Individual test phases
molecule create -s samba      # Create container
molecule converge -s samba    # Run playbook
molecule verify -s samba      # Run tests
molecule destroy -s samba     # Clean up
```

## Test Process

Each Molecule test follows this lifecycle:

1. **Create** - Spin up Fedora container with Podman
2. **Prepare** - Install base packages and dependencies
3. **Converge** - Run the Ansible role being tested
4. **Verify** - Check that services are working correctly
5. **Destroy** - Clean up containers and resources

## Test Environment

### Container Configuration
- **Base Image**: `quay.io/fedora/fedora:latest`
- **Runtime**: Podman with systemd support
- **Privileges**: Elevated (required for systemd services)
- **Networking**: Isolated molecule network

### Mock Data
- **Storage**: Mock directories replace real mount points
- **Credentials**: Test passwords and user accounts
- **Configuration**: Simplified settings for testing

### Port Mappings
- **8080** - VueTorrent/qBittorrent WebUI
- **9090** - Cockpit Web Console
- **445** - Samba/SMB 
- **2049** - NFS
- **111** - NFS Portmapper

## Verification Tests

### Samba Tests
- ✅ Container is running
- ✅ Port 445 accessible
- ✅ User accounts configured
- ✅ Storage directories mounted
- ✅ WSDD2 discovery service

### NFS Tests  
- ✅ Container is running
- ✅ Port 2049 accessible
- ✅ Exports are configured
- ✅ RPC services running
- ✅ Mount points accessible

### VueTorrent Tests
- ✅ Container is running
- ✅ WebUI accessible (port 8080)
- ✅ Downloads directory structure
- ✅ qBittorrent API responding
- ✅ BitTorrent ports available

### Cockpit Tests
- ✅ Package installed
- ✅ Socket service active
- ✅ WebUI accessible (port 9090)
- ✅ Firewall rules configured
- ✅ System integration working

## Troubleshooting

### Common Issues

**Molecule not found**
```bash
pip install molecule[podman]
```

**Podman not available**
```bash
# Fedora/RHEL
sudo dnf install podman

# Ubuntu/Debian  
sudo apt install podman
```

**Container creation fails**
```bash
# Check Podman status
podman system info

# Test container creation
podman run --rm fedora:latest echo "test"
```

**Port conflicts**
```bash
# Check what's using ports
ss -tulpn | grep :8080

# Stop conflicting services
sudo systemctl stop service-name
```

### Debugging Tests

```bash
# Keep containers running after test
molecule test --destroy=never

# Connect to test container
molecule login -s samba

# Check container logs
podman logs samba-server

# Run individual test phases
molecule create -s samba
molecule converge -s samba
# ... debug issues ...
molecule destroy -s samba
```

### Logs and Output

```bash
# Molecule logs
molecule test -s samba -v

# Container service logs  
podman logs container-name

# Systemd service logs (in container)
podman exec container-name journalctl -u service-name
```

## CI/CD Integration

Add to your CI pipeline:

```yaml
# GitHub Actions example
- name: Run Molecule Tests
  run: |
    pip install -r requirements.txt
    ./run-ansible.py test
    ./run-ansible.py test --scenario samba
    ./run-ansible.py test --scenario nfs
```

## Limitations

### What Molecule Tests Successfully ✅
- **Role syntax and structure** - All Ansible role configurations
- **Package installation** - Software dependencies and requirements
- **File and directory creation** - Configuration files and directory structures  
- **Container deployment** - Podman/Docker container creation and management
- **Variable templating** - Ansible variable substitution and templating
- **Task execution flow** - Role task sequence and logic

### What Molecule Cannot Test ⚠️
- **SystemD services** - Requires systemd-enabled containers (containers use `sleep infinity`)
- **Real hardware encryption** - LUKS requires actual block devices
- **Physical storage mounting** - Filesystem operations need real storage
- **Network discovery** - Full mDNS/Avahi in containers is limited
- **Performance** - Container testing doesn't reflect real-world performance

### What This Means
- **Configuration validation** ✅ - Molecule verifies role structure and package installation
- **Service testing** ⚠️ - SystemD services require manual testing on target systems
- **Hardware roles** ⚠️ - (encrypt, mount) require manual testing on real hardware
- **Production deployment** - Use Molecule for development, real testing for production

## Best Practices

### Test Development
1. **Start simple** - Basic container and service startup
2. **Add verification** - Check ports, processes, configuration
3. **Test integration** - Verify services work together
4. **Mock dependencies** - Use fake data for hardware components

### Test Maintenance
1. **Keep tests fast** - Optimize container startup time
2. **Clean up resources** - Always destroy test containers
3. **Update regularly** - Keep base images and dependencies current
4. **Document changes** - Update tests when roles change

## Integration with Main Deployment

Molecule testing complements but doesn't replace real deployment testing:

1. **Development** - Use Molecule for rapid iteration
2. **CI/CD** - Automated testing of role changes
3. **Production** - Deploy to real hardware after Molecule validation
4. **Troubleshooting** - Use Molecule to isolate service issues

The goal is to catch configuration and service issues early, before deploying to production NAS servers.
