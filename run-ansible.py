#!/usr/bin/env python3
"""
Simplified Ansible runner for NAS server deployment
Provides secure vault management and streamlined execution
"""

import os
import sys
import subprocess
import argparse
import secrets
import string
from pathlib import Path
import hashlib
import tempfile


class AnsibleRunner:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.vault_password = None
        self.vault_password_file = None
        
    def generate_vault_password(self, length=32):
        """Generate a secure vault password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
    
    def get_vault_password_file(self):
        """Create or get vault password file"""
        vault_file = self.script_dir / ".vault_pass"
        
        if not vault_file.exists():
            print("🔐 No vault password file found. Generating new secure password...")
            password = self.generate_vault_password()
            
            # Write password to file
            vault_file.write_text(password)
            vault_file.chmod(0o600)
            
            print(f"✅ Generated new vault password and saved to {vault_file}")
            print(f"🔑 Your vault password: {password}")
            print("📝 Please save this password securely - you'll need it to decrypt your vault!")
            print()
            
        return str(vault_file)
    
    def get_vault_template(self):
        """Generate vault file template with secure defaults"""
        template = """---
# Encrypted variables for NAS server deployment
# Edit this file with: ansible-vault edit group_vars/nas_servers/vault.yml

# Ansible become password (sudo password for remote user)
vault_become_password: "your_sudo_password_here"

# Samba user credentials
vault_samba_users:
  - username: "admin"
    password: "admin_secure_password_here"
    uid: "1001"
  - username: "user"
    password: "user_secure_password_here"
    uid: "1002"
"""
        return template
    
    def create_vault_file(self):
        """Create new vault file with template"""
        vault_dir = self.script_dir / "group_vars" / "nas_servers"
        vault_file = vault_dir / "vault.yml"
        
        # Ensure directory exists
        vault_dir.mkdir(parents=True, exist_ok=True)
        
        if vault_file.exists():
            response = input(f"⚠️  Vault file {vault_file} already exists. Overwrite? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("❌ Cancelled vault creation")
                return False
        
        # Create temporary file with template
        template = self.get_vault_template()
        temp_file = self.script_dir / f".vault_temp_{os.getpid()}"
        
        try:
            temp_file.write_text(template)
            
            # Get vault password file
            vault_password_file = self.get_vault_password_file()
            
            # Use ansible-vault to encrypt the template
            cmd = [
                "ansible-vault", "encrypt",
                "--vault-password-file", vault_password_file,
                str(temp_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Move encrypted file to final location
                temp_file.rename(vault_file)
                vault_file.chmod(0o600)
                
                print(f"✅ Created encrypted vault file: {vault_file}")
                print("📝 Edit with: ansible-vault edit group_vars/nas_servers/vault.yml")
                print("🔧 Or use: ./run-ansible.py --edit-vault")
                return True
            else:
                print(f"❌ Failed to encrypt vault file: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating vault file: {e}")
            return False
        finally:
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()
    
    def edit_vault_file(self):
        """Edit existing vault file"""
        vault_file = self.script_dir / "group_vars" / "nas_servers" / "vault.yml"
        
        if not vault_file.exists():
            print(f"❌ Vault file not found: {vault_file}")
            print("💡 Create one first with: ./run-ansible.py --create-vault")
            return False
        
        try:
            # Get vault password file
            vault_password_file = self.get_vault_password_file()
            
            # Use ansible-vault to edit
            cmd = [
                "ansible-vault", "edit",
                "--vault-password-file", vault_password_file,
                str(vault_file)
            ]
            
            print(f"📝 Opening vault file for editing: {vault_file}")
            result = subprocess.run(cmd)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error editing vault file: {e}")
            return False
    
    def check_ansible_structure(self):
        """Verify required Ansible directory structure"""
        required_files = [
            "ansible.cfg",
            "site.yml",
            "inventory/hosts.ini",
            "roles",
            "group_vars"
        ]
        
        required_dirs = [
            "roles/samba-server",
        ]
        
        missing = []
        
        for item in required_files:
            path = self.script_dir / item
            if not path.exists():
                missing.append(item)
        
        for item in required_dirs:
            path = self.script_dir / item
            if not path.is_dir():
                missing.append(item)
                
        if missing:
            print("❌ Missing required Ansible structure:")
            for item in missing:
                print(f"   - {item}")
            return False
            
        print("✅ Ansible directory structure validated")
        return True
    
    def run_discovery(self, args):
        """Run storage discovery playbook"""
        print("🔍 Discovering storage devices...")
        
        # Use discovery playbook
        discovery_args = type('Args', (), {
            'playbook': 'discover-storage.yml',
            'write': True,  # Discovery is safe to run
            'verbose': args.verbose,
            'host': args.host,
            'syntax': False,
            'raw': None
        })()
        
        success = self.run_ansible_command(discovery_args)
        
        if success:
            template_file = self.script_dir / "discovered_storage_template.yml"
            if template_file.exists():
                print(f"✅ Storage discovery completed!")
                print(f"📄 Template generated: {template_file}")
                print("📝 Next steps:")
                print("   1. Review the generated template")
                print("   2. Import or copy sections to storage_config.yml")
                print("   3. Configure mount points, encryption, and services")
        
        return success

    def run_molecule_test(self, args):
        """Run Molecule tests"""
        # Available test scenarios
        scenarios = ["default", "samba", "nfs", "vuetorrent", "cockpit"]
        
        if hasattr(args, 'scenario') and args.scenario:
            if args.scenario not in scenarios:
                print(f"❌ Unknown test scenario: {args.scenario}")
                print(f"Available scenarios: {', '.join(scenarios)}")
                return False
            test_scenario = args.scenario
        else:
            test_scenario = "default"
            
        print(f"🧪 Running Molecule test scenario: {test_scenario}")
        
        # Build molecule command
        cmd = ["molecule", "test"]
        
        # Add scenario if not default
        if test_scenario != "default":
            cmd.extend(["-s", test_scenario])
            
        # Add verbosity
        if args.verbose > 0:
            cmd.append("-" + "v" * min(args.verbose, 3))
            
        print(f"🚀 Executing: {' '.join(cmd)}")
        print()
        
        # Change to script directory
        os.chdir(self.script_dir)
        
        # Execute molecule command
        try:
            result = subprocess.run(cmd, check=True)
            print()
            print(f"✅ Molecule test '{test_scenario}' completed successfully!")
            print("🎉 All containerized services are working correctly!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Molecule test failed with exit code {e.returncode}")
            return False
        except KeyboardInterrupt:
            print("\n⏹️  Test interrupted by user")
            return False
        except FileNotFoundError:
            print("❌ Molecule not found. Install with: pip install molecule[podman]")
            return False

    def run_ansible_command(self, args):
        """Execute ansible-playbook with proper arguments"""
        cmd = ["ansible-playbook"]
        
        # Add playbook file
        cmd.append(args.playbook)
        
        # Add vault password file
        if self.vault_password_file:
            cmd.extend(["--vault-password-file", self.vault_password_file])
        
        # Add verbosity
        if args.verbose > 0:
            cmd.append("-" + "v" * min(args.verbose, 4))
        
        # Add host limit
        if args.host:
            cmd.extend(["-l", args.host])
            
        # Add check mode (dry run) unless --write is specified
        if not args.write:
            cmd.append("--check")
            print("🔍 Running in CHECK MODE (dry run). Use -w/--write to apply changes.")
        else:
            print("✍️  Running in WRITE MODE - changes will be applied!")
            
        # Add syntax check
        if args.syntax:
            cmd.append("--syntax-check")
            print("📝 Running syntax check only")
        
        # Add raw ansible flags if specified
        if hasattr(args, 'raw') and args.raw:
            raw_flags = args.raw.split()
            cmd.extend(raw_flags)
            print(f"🔧 Added raw flags: {' '.join(raw_flags)}")
        
        print(f"🚀 Executing: {' '.join(cmd)}")
        print()
        
        # Change to script directory
        os.chdir(self.script_dir)
        
        # Execute command
        try:
            result = subprocess.run(cmd, check=True)
            print()
            if args.syntax:
                print("✅ Syntax check passed!")
            elif not args.write:
                print("✅ Check mode completed successfully!")
            else:
                print("✅ Playbook execution completed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed with exit code {e.returncode}")
            return False
        except KeyboardInterrupt:
            print("\n⏹️  Execution interrupted by user")
            return False
    
    def main(self):
        parser = argparse.ArgumentParser(
            description="Simplified Ansible runner for NAS server deployment",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s                           # Dry run with site.yml
  %(prog)s -w                        # Apply changes with site.yml  
  %(prog)s -s                        # Syntax check only
  %(prog)s -v 2 -w                   # Apply with verbose level 2
  %(prog)s -p cockpit.yml -w         # Run specific playbook
  %(prog)s --host nas-server -w      # Target specific host
  %(prog)s --host nas-server -v 3    # Dry run specific host with max verbosity
  %(prog)s --discover --host nas-1   # Discover storage on specific host
  %(prog)s --raw="--tags samba"      # Run with raw ansible flags
  %(prog)s test                      # Run all Molecule tests
  %(prog)s test --scenario samba     # Test only Samba role
            """
        )
        
        parser.add_argument(
            "-w", "--write", 
            action="store_true",
            help="Apply changes (default is dry run/check mode)"
        )
        
        parser.add_argument(
            "-v", "--verbose",
            type=int,
            default=0,
            choices=[0, 1, 2, 3, 4],
            help="Verbosity level (0-4, equivalent to -v through -vvvv)"
        )
        
        parser.add_argument(
            "-p", "--playbook",
            default="site.yml",
            help="Playbook file to run (default: site.yml)"
        )
        
        parser.add_argument(
            "--host",
            help="Target specific host or group"
        )
        
        parser.add_argument(
            "-s", "--syntax",
            action="store_true", 
            help="Run syntax check only"
        )
        
        parser.add_argument(
            "--generate-password",
            action="store_true",
            help="Generate new vault password and exit"
        )
        
        parser.add_argument(
            "--create-vault",
            action="store_true",
            help="Create new vault file with template"
        )
        
        parser.add_argument(
            "--edit-vault",
            action="store_true", 
            help="Edit existing vault file"
        )
        
        parser.add_argument(
            "--discover",
            action="store_true",
            help="Discover storage devices on target hosts"
        )
        
        parser.add_argument(
            "--raw",
            help="Pass raw flags to ansible-playbook (e.g., --raw='--tags nfs --diff')"
        )
        
        parser.add_argument(
            "command",
            nargs="?",
            choices=["test"],
            help="Special commands: 'test' runs Molecule tests"
        )
        
        parser.add_argument(
            "--scenario",
            choices=["default", "samba", "nfs", "vuetorrent", "cockpit"],
            help="Molecule test scenario to run (default: default)"
        )
        
        args = parser.parse_args()
        
        print("🏠 NAS Server Ansible Runner")
        print("=" * 40)
        
        # Handle vault operations
        if args.generate_password:
            password = self.generate_vault_password()
            print(f"🔑 Generated secure vault password: {password}")
            return
            
        if args.create_vault:
            success = self.create_vault_file()
            sys.exit(0 if success else 1)
            
        if args.edit_vault:
            success = self.edit_vault_file()
            sys.exit(0 if success else 1)
            
        if args.discover:
            success = self.run_discovery(args)
            sys.exit(0 if success else 1)
            
        # Handle test command
        if args.command == "test":
            success = self.run_molecule_test(args)
            sys.exit(0 if success else 1)
        
        # Check directory structure
        if not self.check_ansible_structure():
            sys.exit(1)
        
        # Verify playbook exists
        playbook_path = self.script_dir / args.playbook
        if not playbook_path.exists():
            print(f"❌ Playbook not found: {args.playbook}")
            sys.exit(1)
        
        # Get vault password file
        try:
            self.vault_password_file = self.get_vault_password_file()
        except Exception as e:
            print(f"❌ Error setting up vault password: {e}")
            sys.exit(1)
            
        # Run ansible command
        success = self.run_ansible_command(args)
        
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    runner = AnsibleRunner()
    runner.main()
