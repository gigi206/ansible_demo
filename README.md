# Ansible

<!-- TOC -->

- [Ansible](#ansible)
    - [Tutorials](#tutorials)
    - [Performance](#performance)
    - [Installation](#installation)
    - [Version](#version)
    - [Development](#development)
    - [SSH](#ssh)
        - [Copy key](#copy-key)
        - [Agent](#agent)
    - [Inventory](#inventory)
        - [Environment variables](#environment-variables)
    - [Cli](#cli)
        - [ansible-inventory](#ansible-inventory)
        - [ansible-playbook](#ansible-playbook)
        - [ansible-config](#ansible-config)
            - [List all configuration options](#list-all-configuration-options)
            - [Dump all configuration options](#dump-all-configuration-options)
            - [View current configuration](#view-current-configuration)
            - [Generate configuration file](#generate-configuration-file)
        - [ansible-pull](#ansible-pull)
        - [ansible-doc](#ansible-doc)
        - [ansible](#ansible)
        - [ansible-galaxy](#ansible-galaxy)
        - [ansible-vault](#ansible-vault)
        - [ansible-lint](#ansible-lint)
    - [Import / Include](#import--include)
    - [Roles](#roles)
    - [Collections](#collections)
    - [Variables](#variables)
        - [Special variables](#special-variables)
            - [omit](#omit)
    - [Loop](#loop)
    - [Query / Lookup](#query--lookup)
    - [Conditions](#conditions)
    - [Error handling in playbooks](#error-handling-in-playbooks)
    - [Block](#block)
    - [Timeout](#timeout)
    - [Strategy](#strategy)
    - [Filters](#filters)
        - [community.general.groupby_as_dict](#communitygeneralgroupby_as_dict)
    - [Custom module](#custom-module)
    - [Modules](#modules)
        - [ansible.builtin.ping](#ansiblebuiltinping)
        - [ansible.builtin.raw](#ansiblebuiltinraw)
        - [ansible.builtin.shell](#ansiblebuiltinshell)
        - [ansible.builtin.async_status](#ansiblebuiltinasync_status)
        - [module ansible.builtin.setup](#module-ansiblebuiltinsetup)
        - [ansible.builtin.gather_facts](#ansiblebuiltingather_facts)
        - [ansible.builtin.debug](#ansiblebuiltindebug)
        - [ansible.builtin.service](#ansiblebuiltinservice)
        - [ansible.builtin.user](#ansiblebuiltinuser)
        - [ansible.builtin.group](#ansiblebuiltingroup)
        - [ansible.builtin.file](#ansiblebuiltinfile)
        - [module ansible.builtin.stat](#module-ansiblebuiltinstat)
        - [ansible.builtin.lineinfile](#ansiblebuiltinlineinfile)
        - [ansible.builtin.blockinfile](#ansiblebuiltinblockinfile)
        - [module ansible.builtin.template](#module-ansiblebuiltintemplate)
        - [ansible.posix.synchronize](#ansibleposixsynchronize)
        - [ansible.builtin.copy](#ansiblebuiltincopy)
        - [ansible.builtin.fetch](#ansiblebuiltinfetch)
        - [ansible.builtin.reboot](#ansiblebuiltinreboot)
        - [ansible.builtin.include_vars](#ansiblebuiltininclude_vars)
        - [ansible.posix.authorized_key](#ansibleposixauthorized_key)
        - [ansible.builtin.expect](#ansiblebuiltinexpect)
        - [ansible.builtin.fail](#ansiblebuiltinfail)
        - [ansible.builtin.assert](#ansiblebuiltinassert)
        - [ansible.builtin.meta](#ansiblebuiltinmeta)
    - [Testing](#testing)
        - [Molecule](#molecule)
        - [ansible-test](#ansible-test)
            - [sanity](#sanity)
            - [units](#units)
            - [coverage](#coverage)
        - [Unit Tests](#unit-tests)
        - [Testinfra](#testinfra)

<!-- /TOC -->

## Tutorials
* [Playlist Ansible Xavki](https://www.youtube.com/playlist?list=PLn6POgpklwWoCpLKOSw3mXCqbRocnhrh-)
* https://devopssec.fr/article/introduction-cours-complet-ansible#begin-article-section

## Performance
* [Mitogen](https://mitogen.networkgenomics.com/ansible_detailed.html)

## Installation
```shell
$ python3 -m venv env
source env/bin/activate
(ansible) $ pip install ansible
(ansible) $  which ansible
/home/gigi/Documents/python/ansible/env/bin/ansible
(ansible) $ deactivate
$
```

## Version
```shell
$ ansible --version
ansible [core 2.15.6]
  config file = None
  configured module search path = ['/home/gigi/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /home/gigi/Documents/python/ansible/env/lib/python3.11/site-packages/ansible
  ansible collection location = /home/gigi/.ansible/collections:/usr/share/ansible/collections
  executable location = /home/gigi/Documents/python/ansible/env/bin/ansible
  python version = 3.11.6 (main, Oct  8 2023, 05:06:43) [GCC 13.2.0] (/home/gigi/Documents/python/ansible/env/bin/python3)
  jinja version = 3.1.2
  libyaml = True
```

## Development
* [Interact ansible with python](https://docs.ansible.com/ansible/latest/dev_guide/developing_api.html)
* [Developing plugins](https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html#developing-plugins)
* [Developing dynamic inventory](https://docs.ansible.com/ansible/latest/dev_guide/developing_inventory.html#developing-inventory)
* [Developing modules](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html#developing-modules-general)

## SSH

### Copy key
```shell
ssh-copy-id -i /path/ssh/private_key user@server
```

Edit `.ssh/authorized_keys` and add security options at the beginning of the file (use [authorized_key](https://docs.ansible.com/ansible/latest/collections/ansible/posix/authorized_key_module.html) module to deploy with Ansible):
```
from="192.168.1.1",no-X11-forwarding ssh-rsa ...
```

See also:
* https://www.jamieweb.net/blog/restricting-and-locking-down-ssh-users/

### Agent
* Add:
```shell
$ eval $(ssh-agent)
$ ssh-add
$ ssh-add -l
$ ps -p ${SSH_AGENT_PID}
```

* SSH config `~/.ssh/config`:
```yaml
Host *
  User ansible
  Port 22
  IdentityFile /path/ssh/private_key
  LogLevel INFO
  Compression yes
  ForwardAgent yes
  ForwardX11 yes

Host bastion
   User username
   Hostname bastion.example.com

Host private-server-*.example.com
   ProxyJump bastion
```

* Or you can add to the inventory these lines to use a ssh bastion:
```yaml
ansible_user: vagrant
ansible_ssh_common_args: -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ProxyCommand="ssh -p 22 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -W %h:%p -q vagrant@bastion"
```

## Inventory
* [Documentation](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html)
* [Building inventory](https://docs.ansible.com/ansible/latest/getting_started/get_started_inventory.html)

* [Patterns](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html#common-patterns)
* [Parameters](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html#connecting-to-hosts-behavioral-inventory-parameters)

* Variable `ANSIBLE_INVENTORY`:
```shell
export ANSIBLE_INVENTORY="$PWD/ansible_hosts"
```

* Or use argument `-i` from ansible command:
```shell
ansible -i ./ansible_hosts
```

* Or by default in `/etc/ansible/hosts`

* Example of inventory:
```yaml
ungrouped:
  hosts:
    mail.example.com:
dbservers:
  hosts:
    foo.example.com:
    bar.example.com:
webservers:
  hosts:
    www[01:50:2].example.com:
    webserver01:
      ansible_host: 192.0.2.140
      http_port: 80
    webserver02:
      ansible_host: 192.0.2.150
      http_port: 443
  vars:
    ansible_user: my_server_user
    ntp_server: ntp.atlanta.example.com
east:
  hosts:
    foo.example.com:
    one.example.com:
    two.example.com:
west:
  hosts:
    bar.example.com:
    three.example.com:
prod:
  children:
    east:
test:
  children:
    west:
```

* Example of inventory for localhost:
```yaml
ungrouped:
  hosts:
    localhost:
      host: 127.0.0.1
      ansible_connection: local
      ansible_python_interpreter: /usr/bin/env python3
```

Or also use from command line `-c local` or `--connection=local` (Cf https://docs.ansible.com/ansible/latest/collections/ansible/builtin/#connection-plugins):
```shell
ansible -i "127.0.0.1," all -c=local -m ping
```

### Environment variables
* [Documentation](https://docs.ansible.com/ansible/latest/reference_appendices/python_3_support.html)
* `ansible_python_interpreter`: `/usr/bin/python3`

```shell
ansible localhost -m ping -e 'ansible_python_interpreter=/usr/bin/python3'
```

## Cli

### ansible-inventory
* [Documentation](https://docs.ansible.com/ansible/latest/cli/ansible-inventory.html):
```shell
$ ansible-inventory --list
$ ansible-inventory --list --yaml
$ ansible-inventory --list --graph
$ ansible-inventory --list --graph --vars
```

### ansible-playbook
* [Keywords](https://docs.ansible.com/ansible/latest/reference_appendices/playbooks_keywords.html)

### ansible-config
* [Documentation location files](https://docs.ansible.com/ansible/latest/reference_appendices/config.html)

* `ANSIBLE_CONFIG`: environment variable if set
* `ansible.cfg`: in the current directory
* `~/.ansible.cfg`: in the home directory
* `/etc/ansible/ansible.cfg`

* Generate a a configuration file:
```shell
ansible-config init --disabled > ansible.cfg
```

#### List all configuration options
* Print all config options:
```shell
$ ansible-config list -t all
$ ansible-config list -t become
```

#### Dump all configuration options
* Dump configuration:
```shell
$ ansible-config dump -t all
$ ansible-config dump -t become
$ ansible-config dump --only-changed -t all
```

#### View current configuration
* View configuration file:
```shell
$ ansible-config view
```

#### Generate configuration file
```shell
$ ansible-config init --disabled > ansible.cfg
$ ansible-config init -t shell --disabled > ansible.cfg
```

### ansible-pull
* [Documentation](https://docs.ansible.com/ansible/latest/cli/ansible-pull.html)
* [Example](https://github.com/jktr/ansible-pull-example)

### ansible-doc
* List all callback
```shell
$ ansible-doc -t callback -l
$ ansible-doc -t callback -F
$ ansible-doc -t module -l
```

* Detail how to use a specific callback:
```shell
ansible-doc -t callback ansible.posix.json
```

* Use `ANSIBLE_STDOUT_CALLBACK` env var to change the callback for the playbook:
```shell
ANSIBLE_STDOUT_CALLBACK=ansible.posix.json ansible-playbook playbook.yaml
```

### ansible
```shell
$ ansible all --ssh-extra-args="-o 'PreferredAuthentications=password'" -m ping
$ ansible -i "127.0.0.1," all -k -K -b -m raw -a "id -u" -o
$ ansible -i "127.0.0.1," all -e "who=world" -m debug -a msg="'Hello {{ who }}'"
$ ansible -i "127.0.0.1," all -m command -a "uptime"
$ ansible -i "127.0.0.1," all -m shell -a "getent passwd | egrep -w root"
```

### ansible-galaxy
* [Cli](https://docs.ansible.com/ansible/latest/cli/ansible-galaxy.html)
* [Galaxy](https://galaxy.ansible.com/ui/)
* [User Guide](https://docs.ansible.com/ansible/latest/galaxy/user_guide.html)

* Create an empty role structure:
```shell
ansible-galaxy init myrole
```

* [Requirements](https://docs.ansible.com/ansible/latest/galaxy/user_guide.html#installing-multiple-roles-from-a-file):
```shell
ansible-galaxy install --roles-path roles -r requirements.yaml
```

### ansible-vault
* [Cli](https://docs.ansible.com/ansible/latest/cli/ansible-vault.html)
* [Vault guide](https://docs.ansible.com/ansible/latest/vault_guide/index.html)
* [Youtube Xavki](https://www.youtube.com/watch?v=ceDcVPuN3HE&list=PLn6POgpklwWoCpLKOSw3mXCqbRocnhrh-&index=60)
* [Youtube Xavki multipassword](https://www.youtube.com/watch?v=m0_2yg4K14w&list=PLn6POgpklwWoCpLKOSw3mXCqbRocnhrh-&index=62)

* Ask password:
```shell
ansible all --ask-vault -m debug -a "var=encrypted_var"
```

* Use a password file:
```shell
ansible all --vault-password-file ./vault_password -m debug -a "var=encrypted_var"
```

* Environment file:
```
export ANSIBLE_VAULT_PASSWORD_FILE=$(realpath ./vault_password)
```

* How to find var files that contain a specific secret ?
```shell
VAR_SEARCH="secret"
$ for file in $(find . -type f -name "*.yaml" -not -path "./env/*" -exec egrep -El '^\$ANSIBLE_VAULT;' {} \;); do ansible-vault view "$file" | egrep -w "^${VAR_SEARCH}:" >/dev/null && echo "$file"; done
./group_vars/all/vault.yaml
$ ansible-vault view ./group_vars/all/vault.yaml
secret: This is very secret!
```

### ansible-lint
* [Documentation](https://ansible.readthedocs.io/projects/lint/)

## Import / Include
* Compare:
  * [Comparing include (dynamic) vs import (static)](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse.html#comparing-includes-and-imports-dynamic-and-static-reuse)
  * [Include vs Import](https://www.ansiblejunky.com/blog/ansible-101-include-vs-import/)

* For static reuse, add an `import_*` task in the tasks section of a play:
  * [import_playbook](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/import_playbook_module.html)
  * [import_role](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/import_role_module.html#import-role-module)
  * [import_tasks](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/import_tasks_module.html#import-tasks-module)

* For dynamic reuse, add an `include_*` task in the tasks section of a play:
  * [include_role](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/include_role_module.html#include-role-module)
  * [include_tasks](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/include_tasks_module.html#include-tasks-module)
  * [include_vars](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/include_vars_module.html#include-vars-module)

If you really want include_role to apply tags to all tasks inside the role, then you need to use the `apply` option:
```yaml
- hosts: localhost
  gather_facts: no

  tasks:
    - name: Apply tags to only this task (include_role)
      include_role:
        name: example
        apply:
          tags:
            - install
      tags:
        - install

    - debug:
        msg: "include_role completed"
      tags:
        - install

    - name: Apply tags to tasks inside the role (import_role)
      import_role:
        name: example
      tags:
        - install
```

And run `ansible-playbook test.yml --tags=install`.

## Roles
* [Documentation](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html)

## Collections
* [Documentation](https://docs.ansible.com/ansible/latest/collections_guide/collections_using_playbooks.html)
* [Comparing standalone roles to collection roles](https://docs.ansible.com/ansible/latest/dev_guide/migrating_roles.html#comparing-standalone-roles-to-collection-roles)

* Structure of an Ansible collection:
```
mynamespace/
└── mycollection/
  ├── docs/
  ├── galaxy.yml
  ├── plugins/
  │   ├── modules/
  │   │   └── module1.py
  │   ├── inventory/
  │   └── .../
  ├── README.md
  ├── roles/
  │   ├── role1/
  │   ├── role2/
  │   └── .../
  ├── playbooks/
  │   ├── files/
  │   ├── vars/
  │   ├── templates/
  │   └── tasks/
  └── tests/
  ```

* To create a collection with roles:
```shell
$ mkdir collections/ansible_collections/
$ cd collections/ansible_collections/
$ ansible-galaxy collection init gigix.demo
$ cd gigix/demo
# https://docs.ansible.com/ansible/latest/dev_guide/developing_collections_structure.html#playbooks-directory
$ mkdir playbooks/{files,vars,templates,tasks}
$ cd roles
$ ansible-galaxy init test
```

* Now you need to configure the collection PATH with one of them (cf [documentation](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#envvar-ANSIBLE_COLLECTIONS_PATH)):
  * environment variable: `ANSIBLE_COLLECTIONS_PATH=collections:/usr/share/ansible/collections` 
  * configuration file `ansible.cfg`: `collections_path=collections:/usr/share/ansible/collections`

* [Using a playbook from a collection](https://docs.ansible.com/ansible/latest/collections_guide/collections_using_playbooks.html#using-a-playbook-from-a-collection)

```shell
ansible-playbook my_namespace.my_collection.playbook1 -i ./myinventory
```

In this demo you can try `ansible-playbook -i inventory.yaml -c local gigix.demo.playbook` to call the playbook (cf [gigix.demo.playbook](./collections/ansible_collections/gigix/demo/playbooks/playbook.yml)).

* Call a module and a role from an ansible collection:
```yaml
tasks:
  - name: Test my module
    gigix.demo.mymodule:
      number: 11

  roles:
  - gigix.demo.myrole
```

But if you use references to the same collection and namespace, you can simplify the code without specifying the `collection.namespace` (`gigix.demo`) like that:
```yaml
tasks:
  - name: Test my module
    mymodule:
      number: 11

  roles:
  - myrole
```

## Variables
* [Variables precedence](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html#understanding-variable-precedence)
* [Special variables](https://docs.ansible.com/ansible/latest/reference_appendices/special_variables.html)
* [Variables inside a jinja template](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/template_module.html#synopsis)
* [Xavki Youtube](https://www.youtube.com/watch?v=UuiRDRIJ-sM&list=PLn6POgpklwWoCpLKOSw3mXCqbRocnhrh-&index=10)

### Special variables

#### omit
* [Documentation](https://docs.ansible.com/ansible/latest/playbook_guide/complex_data_manipulation.html#omit-elements-from-a-list)

Examples:
```yaml
id: "{{ (openstack_networks | default({})).id | default(omit) }}"
```

```yaml
id: "{{ omit if openstack_networks.id is not defined else openstack_networks.id }}"
```

```yaml
- name: Touch files with an optional mode
  ansible.builtin.file:
    dest: "{{ item.path }}"
    state: touch
    mode: "{{ item.mode | default(omit) }}"
  loop:
    - path: /tmp/foo
    - path: /tmp/bar
    - path: /tmp/baz
      mode: "0444"
```

## Loop
* [Documentation](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_loops.html)
* [Migrating from with_X to loop](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_loops.html#migrating-from-with-x-to-loop)

* [Loop variables](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_loops.html#extended-loop-variables)
```yaml
loop_control:
  extended: true
```

* Simple loop:
```yaml
- name: Fail if return code is not 0
  ansible.builtin.fail:
    msg: "The command ({{ item.cmd }}) did not have a 0 return code"
  when: item.rc != 0
  loop: "{{ echo.results }}"
```

* `register` and `changed_when`:
```yaml
- name: Place the result of the current item in the variable
  ansible.builtin.shell: echo "{{ item }}"
  loop:
    - one
    - two
  register: echo
  changed_when: echo.stdout != "one"
```

* `until`:
```yaml
- name: Retry a task until a certain condition is met
  ansible.builtin.shell: /usr/bin/foo
  register: result
  until: result.stdout.find("all systems go") != -1
  retries: 5
  delay: 10
```

* `query`:
```yaml
- name: Show all the hosts matching the pattern, ie all but the group www
  ansible.builtin.debug:
    msg: "{{ item }}"
  loop: "{{ query('inventory_hostnames', 'all:!www') }}"
```

* control output with `label`:
```yaml
- name: Create servers
  digital_ocean:
    name: "{{ item.name }}"
    state: present
  loop:
    - name: server1
      disks: 3gb
      ram: 15Gb
      network:
        nic01: 100Gb
        nic02: 10Gb
        ...
  loop_control:
    label: "{{ item.name }}"
```

* Add `pause` between loop:
```yaml
- name: Create servers, pause 3s before creating next
  community.digitalocean.digital_ocean:
    name: "{{ item }}"
    state: present
  loop:
    - server1
    - server2
  loop_control:
    pause: 3
```

* Add an index variable (`index_var` is 0 indexed):
```
- name: Count our fruit
  ansible.builtin.debug:
    msg: "{{ item }} with index {{ my_idx }}"
  loop:
    - apple
    - banana
    - pear
  loop_control:
    index_var: my_idx
```

## Query / Lookup
* [Documentation](https://docs.ansible.com/ansible/latest/plugins/lookup.html)

```yaml
loop: "{{ query('inventory_hostnames', 'all') }}"
loop: "{{ lookup('inventory_hostnames', 'all', wantlist=True) }}"
```

## Conditions
* https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html

* Skip current hostname:
```yaml
when: inventory_hostname != 'hostname_to_exclude'
```

* test condition from a command:
```yaml
- name: Register a variable, ignore errors and continue
  ansible.builtin.command: /bin/false
  register: result
  ignore_errors: true

- name: Run only if the task that registered the "result" variable fails
  ansible.builtin.command: /bin/something
  when: result is failed

- name: Run only if the task that registered the "result" variable succeeds
  ansible.builtin.command: /bin/something_else
  when: result is succeeded

- name: Run only if the task that registered the "result" variable is skipped
  ansible.builtin.command: /bin/still/something_else
  when: result is skipped

- name: Run only if the task that registered the "result" variable changed something.
  ansible.builtin.command: /bin/still/something_else
  when: result is changed
```

* test if not defined
```yaml
- include_tasks: other_tasks.yml
  when: x is not defined

- name: Fail if "bar" is undefined
  ansible.builtin.fail: msg="Bailing out. This play requires 'bar'"
  when: bar is undefined
```

* multiple conditions:
```yaml
- name: Shut down CentOS 6 and Debian 7 systems
  ansible.builtin.command: /sbin/shutdown -t now
  when: (ansible_facts['distribution'] == "CentOS" and ansible_facts['distribution_major_version'] == "6") or
        (ansible_facts['distribution'] == "Debian" and ansible_facts['distribution_major_version'] == "7")
```

* set fact and test from it:
```yaml
- name: Get the CPU temperature
  set_fact:
    temperature: "{{ ansible_facts['cpu_temperature'] }}"

- name: Restart the system if the temperature is too high
  when: temperature | float > 90
  shell: "reboot"
```

* loop condition:
```yaml
- name: Run with items greater than 5
  ansible.builtin.command: echo {{ item }}
  loop: [ 0, 2, 4, 6, 8, 10 ]
  when: item > 5
```

## Error handling in playbooks
* https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_error_handling.html

```yaml
ignore_errors: true
ignore_unreachable: true
```

* [Defining failure](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_error_handling.html#defining-failure)
```yaml
- name: Check if a file exists in temp and fail task if it does
  ansible.builtin.command: ls /tmp/this_should_not_be_here
  register: result
  failed_when:
    - result.rc == 0 or result.rc >= 10
    - '"No such" not in result.stdout'

- name: example of many failed_when conditions with OR
  ansible.builtin.shell: "./myBinary"
  register: ret
  failed_when: >
    ("No such file or directory" in ret.stdout) or
    (ret.stderr != '') or
    (ret.rc == 10)
```

* [Defining changed](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_error_handling.html#defining-changed)
```yaml
- name: Report 'changed' when the return code is not equal to 2
  ansible.builtin.shell: /usr/bin/billybass --mode="take me to the river"
  register: bass_result
  changed_when: "bass_result.rc != 2"

- name: This will never report 'changed' status
  ansible.builtin.shell: wall 'beep'
  changed_when: False

- name: Combine multiple conditions to override 'changed' result
  ansible.builtin.command: /bin/fake_command
  register: result
  ignore_errors: True
  changed_when:
    - '"ERROR" in result.stderr'
    - result.rc == 2
```

* [Ensuring success for command and shell](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_error_handling.html#ensuring-success-for-command-and-shell)
```yaml
- name: Run this command and ignore the result
  ansible.builtin.shell: /usr/bin/somecommand || /bin/true
```

* [Aborting on the first error: any_errors_fatal](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_error_handling.html#aborting-on-the-first-error-any-errors-fatal)
```yaml
- hosts: somehosts
  any_errors_fatal: true
  roles:
    - myrole

- hosts: somehosts
  tasks:
    - block:
        - include_tasks: mytasks.yml
      any_errors_fatal: true
```

* [Setting a maximum failure percentage](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_error_handling.html#setting-a-maximum-failure-percentage)

## Block
* https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_blocks.html
```yaml
- name: Attempt and graceful roll back demo
  block:
    - name: Print a message
      ansible.builtin.debug:
        msg: 'I execute normally'

    - name: Force a failure
      ansible.builtin.command: /bin/false

    - name: Never print this
      ansible.builtin.debug:
        msg: 'I never execute, due to the above task failing, :-('
  rescue:
    - name: Print when errors
      ansible.builtin.debug:
        msg: 'I caught an error'

    - name: Force a failure in middle of recovery! >:-)
      ansible.builtin.command: /bin/false

    - name: Never print this
      ansible.builtin.debug:
        msg: 'I also never execute :-('
  always:
    - name: Always do this
      ansible.builtin.debug:
        msg: "This always executes"
```

## Timeout
* [Documentation](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_async.html)

```yaml
- name: without timeout (check every 2 seconds if the task has finished with a timeout set to 10s)
  ansible.builtin.command:
    cmd: sleep 2
  async: 10
  poll: 2
  changed_when: false

- name: With timeout (check every 1 second to a timeout set to 1 sec)
  ansible.builtin.command:
    cmd: sleep 2
  async: 1
  poll: 1
  changed_when: false
```

## Strategy
* https://docs.ansible.com/ansible/latest/plugins/strategy.html

* List all strategies:
```shell
ansible-doc -t strategy -l
```

## Filters
* [Documentation](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_filters.html)
* [List of filters](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/#filter-plugins)

### community.general.groupby_as_dict
```yaml
- name: Output mount facts grouped by device name
  ansible.builtin.debug:
    var: ansible_facts.mounts | community.general.groupby_as_dict('device')

- name: Output mount facts grouped by mount point
  ansible.builtin.debug:
    var: ansible_facts.mounts | community.general.groupby_as_dict('mount')
```

## Custom module
* https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html

## Modules
* [All](https://docs.ansible.com/ansible/2.9/modules/list_of_all_modules.html)
* [Builtin](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/)
* [Posix](https://docs.ansible.com/ansible/latest/collections/ansible/posix/)
* [Netcommon](https://docs.ansible.com/ansible/latest/collections/ansible/netcommon/index.html)
* [Utils](https://docs.ansible.com/ansible/latest/collections/ansible/utils/index.html)
* [Windows](https://docs.ansible.com/ansible/latest/collections/ansible/windows/index.html)

### ansible.builtin.ping
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/ping_module.html

* Executes a low-down and dirty command:
```shell
ansible-doc -t module ansible.builtin.ping
```

```shell
ansible all -m ping
```

### ansible.builtin.raw
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/raw_module.html

* Executes a low-down and dirty command:
```shell
ansible-doc -t module ansible.builtin.raw
```

```shell
ansible all -i "127.0.0.1," -m raw -a "id -u"
```

### ansible.builtin.shell
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/shell_module.html

* Execute shell commands on targets:
```shell
ansible-doc -t module ansible.builtin.shell
```

```shell
ansible -i "127.0.0.1," all -m shell -a "getent passwd | egrep -w root"
```

### ansible.builtin.async_status
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/async_status_module.html

* Obtain status of asynchronous task:
```yaml
- name: Async (no wait)
  ansible.builtin.command:
    cmd: sleep 10
  async: 20
  poll: 0
  register: _full_async
  changed_when: false

- name: Wait full async task
  ansible.builtin.async_status:
    jid: "{{ _full_async.ansible_job_id }}"
  register: _async_result
  until: _async_result.finished
  retries: 10
  delay: 10
```

### module ansible.builtin.setup
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/setup_module.html

* Gathers facts about remote hosts:
```shell
ansible-doc -t module ansible.builtin.setup
```

```shell
$ ansible all -m setup
$ ansible all -m setup -a 'filter=*ip*'
$ ansible all -m setup -a 'gather_subset=default_ipv4'
```

### ansible.builtin.gather_facts
```shell
ansible-doc -t module ansible.builtin.setup
```

* Gathers facts about remote hosts:
```shell
# Display facts from all hosts and store them indexed by hostname at /tmp/facts.
ansible all -m ansible.builtin.gather_facts --tree /tmp/facts/localhost
```

### ansible.builtin.debug
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/debug_module.html

* Print statements during execution:
```shell
ansible-doc -t module ansible.builtin.debug
```

```shell
$ ansible all -m debug -a msg="'Hello {{ var1 }}'"
$ ansible all -m debug -a var=var1
```

### ansible.builtin.service
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/service_module.html

* Manage services:
```shell
ansible-doc -t module ansible.builtin.service
```

```shell
ansible all -m service -a "name=ssh state=started"
```

### ansible.builtin.user
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/user_module.html

* Manage user accounts:
```shell
ansible-doc -t module ansible.builtin.user
```

```shell
ansible all -m user -a "'name=foo password={{ \'password\' | password_hash(\'sha512\') }}'"
```

### ansible.builtin.group
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/group_module.html

* Add or remove groups:
```shell
ansible-doc -t module ansible.builtin.group
```

```shell
ansible all -m group -a "name=team state=present"
```

### ansible.builtin.file
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/file_module.html

* Manage files and file properties:
```shell
ansible-doc -t module ansible.builtin.file
```

```shell
ansible all -m file -a "dest=/opt/bmc.txt mode=755 owner=ec2-user"
```

### module ansible.builtin.stat
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/stat_module.html

* Retrieve file or file system status:
```shell
ansible-doc -t module ansible.builtin.stat
```

```shell
ansible all -m stat -a "path=/etc/passwd"
```

### ansible.builtin.lineinfile
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/lineinfile_module.html#ansible-collections-ansible-builtin-lineinfile-module

* Manage lines in text files:
```shell
ansible-doc -t module ansible.builtin.lineinfile
```

```shell
ansible all -m ansible.builtin.lineinfile -C -D -a 'dest=/etc/passwd regexp="^root:(.*)$" line="gigix:\1" state=present backrefs=yes backup=yes'
```

```yaml
- name: Create MySQL client config (Debian os family)
  copy:
    dest: "/root/.my.cnf"
    content: |
      [client]
      user=root
      password={{ root_password }}
    mode: 0400
```

### ansible.builtin.blockinfile
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/blockinfile_module.html

* Insert/update/remove a text block surrounded by marker lines
```yaml
- name: Insert/Update "Match User" configuration block in /etc/ssh/sshd_config prepending and appending a new line
  ansible.builtin.blockinfile:
    path: /etc/ssh/sshd_config
    append_newline: true
    prepend_newline: true
    block: |
      Match User ansible-agent
      PasswordAuthentication no

- name: Insert/Update configuration using a local file and validate it
  ansible.builtin.blockinfile:
    block: "{{ lookup('ansible.builtin.file', './local/sshd_config') }}"
    path: /etc/ssh/sshd_config
    backup: yes
    validate: /usr/sbin/sshd -T -f %s
```

### module ansible.builtin.template
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/template_module.html

Additional variables listed below can be used in templates:
* `ansible_managed` (configurable via the defaults section of ansible.cfg) contains a string which can be used to describe the template name, host, modification time of the template file and the owner uid.
* `template_host contains` the node name of the template’s machine.
* `template_uid` is the numeric user id of the owner.
* `template_path` is the path of the template.
* `template_fullpath` is the absolute path of the template.
* `template_destpath` is the path of the template on the remote system (added in 2.8).
* `template_run_date` is the date that the template was rendered.

* Template a file out to a target host
```shell
ansible-doc -t module ansible.builtin.template
```

```yaml
- name: Declare interface ib0
  register: ib0
  template:
    src=files/ifcfg-ib0.j2
    dest=/etc/sysconfig/network/ifcfg-ib0
    owner=root
    group=root
    mode=0644
  with_items:
    - { ip: 192.168.1.{{ ansible_eth0.ipv4.address.split(".")[-1] }}' }
  notify: UP interface ib0
```

### ansible.posix.synchronize
* https://docs.ansible.com/ansible/latest/collections/ansible/posix/synchronize_module.html

* A wrapper around rsync to make common tasks in your playbooks quick and easy:
```shell
ansible-doc -t module ansible.posix.synchronize
```

```yaml
- name: Synchronization using rsync protocol (push)
  ansible.posix.synchronize:
    src: some/relative/path/
    dest: rsync://somehost.com/path/

- name: Synchronization using rsync protocol (pull)
  ansible.posix.synchronize:
    mode: pull
    src: rsync://somehost.com/path/
    dest: /some/absolute/path/

- name:  Synchronization using rsync protocol on delegate host (push)
  ansible.posix.synchronize:
    src: /some/absolute/path/
    dest: rsync://somehost.com/path/
  delegate_to: delegate.host

- name: Synchronization using rsync protocol on delegate host (pull)
  ansible.posix.synchronize:
    mode: pull
    src: rsync://somehost.com/path/
    dest: /some/absolute/path/
  delegate_to: delegate.host
```

### ansible.builtin.copy
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/copy_module.html

* Copy files to remote locations:
```shell
ansible-doc -t module ansible.builtin.copy
```

```shell
ansible all -m copy -a 'src=/tmp/src.txt dest=/tmp/dest.txt'
```

### ansible.builtin.fetch
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/fetch_module.html

* Fetch files from remote nodes:
```shell
ansible-doc -t module ansible.builtin.fetch
```

```shell
ansible all -m fetch -a 'src=/tmp/src.txt dest=/tmp/dest.txt'
```

### ansible.builtin.reboot
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/reboot_module.html
* [Youtube Xavki](https://www.youtube.com/watch?v=SRD2h5Fh4fA&list=PLn6POgpklwWoCpLKOSw3mXCqbRocnhrh-&index=20)

* Reboot a machine:
```shell
ansible-doc -t module ansible.builtin.reboot
```

```shell
ansible all -m reboot -a "reboot_timeout=3600"
```

### ansible.builtin.include_vars
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/include_vars_module.html

* Load variables from files, dynamically within a task:
```shell
ansible-doc -t module ansible.builtin.include_vars
```

* Include vars file from a role and merge all. The last file override the others:
```yaml
- name: Merge all file vars found
  ansible.builtin.include_vars: "{{ item }}"
  loop:
    # - default.yml # use main.yml instead (this is the default file)
    - "{{ ansible_os_family }}.yml"
    - "{{ ansible_distribution }}.yml"
    - "{{ ansible_distribution }}{{ ansible_distribution_version }}.yml"
  when:
    - ([path, item] | path_join) in query("ansible.builtin.fileglob", "{}/*.yml".format(path))
  vars:
    path: "{{ [role_path, 'vars'] | path_join }}"
```

* Include vars file from a role and stop at the 1st file found (don't continue on other files):
```yaml
- name: Include vars with first_found
  ansible.builtin.include_vars: "{{ lookup('ansible.builtin.first_found', params) }}"
  vars:
    params:
      files:
        - "{{ ansible_distribution }}{{ ansible_distribution_version }}.yaml"
        - "{{ ansible_distribution }}.yml"
        - "{{ ansible_os_family }}.yml"
        - default.yml
      paths:
        - "{{ [role_path, 'vars'] | path_join }}"
```

* Or with nested directories structure:
```yaml
- name: Merge all file vars found
  ansible.builtin.include_vars: "{{ item }}"
  loop:
    - "{{ ansible_distribution }}/main.yml"
    - "{{ ansible_distribution }}/{{ ansible_distribution_major_version }}/main.yml"
    - "{{ ansible_distribution }}/{{ ansible_distribution_major_version }}/{{ ansible_distribution_version }}.yml"
  when:
    - ([path, item] | path_join) in query("community.general.filetree", path) | selectattr("state", "in", "file") | map(attribute="src") | list
  vars:
    path: "{{ [role_path, 'vars'] | path_join }}"
```

### ansible.posix.authorized_key
* https://docs.ansible.com/ansible/latest/collections/ansible/posix/authorized_key_module.html

* Adds or removes an SSH authorized key:
```shell
ansible-doc -t module ansible.posix.authorized_key
```

```yaml
- name: Set authorized key taken from file
  ansible.posix.authorized_key:
    user: charlie
    state: present
    key: "{{ lookup('file', '/home/charlie/.ssh/id_rsa.pub') }}"
    key_options: 'no-port-forwarding,from="10.0.1.1"'
```

### ansible.builtin.expect
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/expect_module.html

* Executes a command and responds to prompts:
```shell
ansible-doc -t module ansible.builtin.expect module
```

```yaml
- name: Case insensitive password string match
  ansible.builtin.expect:
    command: passwd username
    responses:
      (?i)password: "MySekretPa$$word"
  # you don't want to show passwords in your logs
  no_log: true
```

### ansible.builtin.fail
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/fail_module.html#ansible-collections-ansible-builtin-fail-module

* Fail with custom message:
```shell
ansible-doc -t module ansible.builtin.fail
```

```shell
ansible all -m ansible.builtin.fail -a "msg='Oops!'"
```

### ansible.builtin.assert
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/assert_module.html

* Asserts given expressions are true:
```shell
ansible-doc -t module ansible.builtin.assert
```

```shell
$ ansible all -m assert -a "that='\'test\' != \'test\'' msg='OMG'"
$ ansible all -m assert -a "that='\'test\' == \'test\'' fail_msg='OMG' success_msg='Bingo'"
```

```yaml
- name: Ensure PAM Displays Last Logon/Access Notification - Check integrity of
    authselect current profile
  ansible.builtin.command:
    cmd: authselect check
  register: result_authselect_check_cmd
  changed_when: false
  failed_when: false

- name: Ensure PAM Displays Last Logon/Access Notification - Informative message
    based on the authselect integrity check result
  ansible.builtin.assert:
    that:
    - result_authselect_check_cmd.rc == 0
    fail_msg:
    - authselect integrity check failed. Remediation aborted!
    - This remediation could not be applied because an authselect profile was
      not selected or the selected profile is not intact.
    - It is not recommended to manually edit the PAM files when authselect tool
      is available.
    - In cases where the default authselect profile does not cover a specific
      demand, a custom authselect profile is recommended.
    success_msg:
    - authselect integrity check passed
```

### ansible.builtin.meta
* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/meta_module.html#parameter-free_form

* Execute Ansible **actions**:
```shell
ansible-doc -t module ansible.builtin.meta
```

```shell
ansible all -m ansible.builtin.meta -a "refresh_inventory"
```
