#!/usr/bin/env python3

from ansible import context
from ansible.module_utils.common.collections import ImmutableDict
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager

from ansible.constants import DEFAULT_VAULT_ID_MATCH
from ansible.parsing.vault import VaultSecret

loader = DataLoader()
vault_password = open('../vault_password', 'r').read().strip()
vault = [(DEFAULT_VAULT_ID_MATCH, VaultSecret(vault_password.encode()))]
loader.set_vault_secrets(vault)
context.CLIARGS = ImmutableDict(tags={}, listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh',
                                module_path=None, forks=100, remote_user='bitv', private_key_file="/Users/an/.ssh/ssh_rsa_keys",
                                ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, become=False,
                                become_method='sudo', become_user='root', verbosity=True, check=False, start_at_task=None)
inventory = InventoryManager(loader=loader, sources='../hosts')
variable_manager = VariableManager(loader=loader, inventory=inventory)
pbex = PlaybookExecutor(playbooks=['../playbook.yaml'], inventory=inventory, variable_manager=variable_manager, loader=loader, passwords={})
results = pbex.run()
