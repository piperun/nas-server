# Fedora CoreOS NAS Server Ansible Project

This project provides a comprehensive, modular Ansible setup for managing a Fedora CoreOS-based NAS server. It includes roles for:

- **Cockpit Web Console Theming**: Fully modular, variable-driven theme system for Cockpit login and UI, including custom CSS, JS, branding, and background images, with container mount and systemd override management.
- **Storage Management**: Automated discovery, configuration, and mounting of storage devices.
- **Encryption**: LUKS encryption setup and keyfile management.
- **NFS Server**: Export and manage NFS shares.
- **Samba Server**: Export and manage Samba shares.
- **VueTorrent**: Automated deployment and configuration of VueTorrent (qBittorrent Web UI).

## Features
- **Idempotent, modular roles** for each service/component
- **Variable-driven configuration** (see `group_vars/`)
- **Automated Cockpit theming** with dynamic backgrounds, fade-in effects, and persistent randomization
- **Systemd override and container mount management** for Cockpit
- **Storage and encryption auto-discovery**
- **Comprehensive documentation** (see below)

## Quick Start
1. Clone this repo and review/edit `group_vars/nas_servers/vars.yml` for your environment.
2. Place your theme files under `files/theme/<theme_name>/` as described in the docs.
3. Run:
   ```sh
   ./run-ansible.py -w
   ```
4. Access Cockpit at `https://<your-nas-ip>:9090/`.

## Documentation
All detailed documentation is now in the `doc/` directory. See:

- [MOLECULE_TESTING.md](doc/MOLECULE_TESTING.md) - Testing strategy and scenarios
- [STORAGE_CONFIG_GUIDE.md](doc/STORAGE_CONFIG_GUIDE.md) - Storage configuration and best practices
- [VAULT_SETUP.md](doc/VAULT_SETUP.md) - Vault and secrets management

Other markdown files:
- [README.md](doc/README.md) (this file)

## Directory Structure
```
roles/
  cockpit_theme/   # Cockpit theming role
  storage/         # Storage management
  encrypt/         # Encryption setup
  nfs-server/      # NFS exports
  samba-server/    # Samba exports
  vuetorrent/      # VueTorrent deployment
files/
  theme/<theme_name>/assets/      # Theme CSS/JS
  theme/<theme_name>/branding/    # Branding files
  theme/<theme_name>/images/      # Background images
```

## Useful Links
- [Cockpit Project](https://cockpit-project.org/)
- [Fedora CoreOS](https://getfedora.org/coreos/)
- [Ansible Documentation](https://docs.ansible.com/)

## License
MIT
