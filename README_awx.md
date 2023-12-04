# AWX / TOWER
## Documentation
* [Tower](https://docs.ansible.com/ansible-tower/latest/html/)
* [Ansible](https://ansible.readthedocs.io/projects/awx/en/latest/)

## Variable precedence hierarchy
![Ansible AWX Variable Precedence Hierarchy](https://docs.ansible.com/ansible-tower/latest/html/userguide/_images/Architecture-Tower_Variable_Precedence_Hierarchy.png)

## Tuto
### Change admin password
```shell
kubectl -n awx-operator exec -it deployments/awx-web -c awx-web -- awx-manage changepassword admin
Changing password for user 'admin'
Password:
Password (again):
Password changed successfully for user 'admin'
```

### Adding an external database
* https://blog.stephane-robert.info/post/ansible-awx-operator-external-database/

### Add callback plugins
* https://docs.ansible.com/ansible-tower/latest/html/administration/tipsandtricks.html#using-callback-plugins-with-tower

### AWX environment
AWX automatically adds the following variables to the job environment:
* [Environment](https://docs.ansible.com/ansible-tower/latest/html/userguide/job_templates.html#launch-a-job-template)

### Job template callback url
* *IMPORTANT*: You must adding in `Settings` > `Miscellaneous System settings` > `Remote Host Headers` the value `HTTP_X_FORWARDED_FOR`:
```yaml
[
  "REMOTE_ADDR",
  "REMOTE_HOST",
  "HTTP_X_FORWARDED_FOR"
]
```

* https://docs.ansible.com/ansible-tower/latest/html/userguide/job_templates.html#provisioning-callbacks
```shell
$ curl -L -k -i -f --data "host_config_key=cfbaae23-81c0-47f8-9a40-44493b82f06a" https://awx.gigix/api/v2/job_templates/10/callback/
$ curl -f -H 'Content-Type: application/json' -XPOST \
                 -d '{"host_config_key": "5a8ec154832b780b9bdef1061764ae5a", "extra_vars": "{\"foo\": \"bar\"}"}' \
                 http://<TOWER_SERVER_NAME>/api/v2/job_templates/1/callback
```

### Use a ssh bastion to a host
Inside the host or group, add to vars where `192.168.121.94` is the ip of the host bastion:
```yaml
ansible_user: vagrant
ansible_ssh_common_args: -o StrictHostKeyChecking=no -o ProxyCommand="ssh -p 22 -o StrictHostKeyChecking=no -o 'ForwardAgent yes' -W %h:%p -q vagrant@192.168.121.94"
```

* [Jumphost with a custom credential](https://github.com/IBM/IBMDeveloper-recipes/blob/main/multiple-jumphosts-in-ansible-tower-part-1/index.md)
  * don't forget to add to your host: `ansible_ssh_common_args: '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ProxyCommand="ssh -W %h:%p -p {{ jh_ssh_port }} {{ jh_ssh_user }}@{{ jh_ip }} -i $JH_SSH_PRIVATE_KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"'`
  * [Multiple jumphost](https://github.com/IBM/IBMDeveloper-recipes/blob/main/multiple-jumphosts-in-ansible-tower-part-1/index.md#4-configuring-host-variables)

### Instance type
* https://blog.stephane-robert.info/post/ansible-awx-add-isolated-execution-node/
* https://github.com/ansible/awx/blob/devel/docs/execution_nodes.md
```
                                                     AWX TASK POD
                                                   ┌──────────────┐
                                                   │              │
                                                   │ ┌──────────┐ │
┌─────────────────┐   ┌─────────────────┐          │ │ awx-task │ │
│execution node 2 ├──►│     hop node    │◄────┐    │ ├──────────┤ │
└─────────────────┘   ├─────────────────┤     ├────┼─┤ awx-ee   │ │
                      │ execution node 1│◄────┘    │ └──────────┘ │
                      └─────────────────┘ Receptor │              |
                                            TCP    └──────────────┘
                                           Peers
```

| instance name    | listener_port    | peers_from_control_nodes | peers        |
| :--------------- | :--------------- | :----------------------- | :----------- |
| execution node 1 | 27199 	          | true                     | []           |
| hop node         | 27199            | true                     | []           |
| execution node 2 | null             | false                    | ["hop node"] |

## Cli
* [Cli](https://docs.ansible.com/ansible-tower/latest/html/towercli/index.html)
* [Examples](https://blog.stephane-robert.info/post/ansible-cli-tower-gitlab-ci-cd/)
* [Youtube](https://youtu.be/57HDybbeQvQ)

### Install
* [Documentation](https://docs.ansible.com/ansible-tower/latest/html/towercli/usage.html#installation)
* Prefer install with:
```shell
pip install --user awxkit
```

### login
```shell
eval $(awx login -k --conf.host https://awx.gigix --conf.username admin --conf.password p@assword -f human)
```

Or with the token:
```shell
awx -k --conf.token nBuUAFRfhjSHQxClRgrK6Hmi7UG8gS jobs list
```

Or with the API key generated on https://awx.gigix/#/users/1/tokens:
```shell
export TOWER_HOST=https://awx.gigix
export TOWER_VERIFY_SSL=false
export TOWER_OAUTH_TOKEN=nBuUAFRfhjSHQxClRgrK6Hmi7UG8gS
```

See also variable `TOWER_USERNAME` and `TOWER_PASSWORD`.

### job
* List job with coulumns `id`, `name` and `status`:
```shell
awx -k job list -f human --filter "id,name,status"
```

* List only jobs with name `ansible_demo`:
```shell
awx job list --name ansible_demo -f human --filter "id,name,status"
```

* Print stdout of the job id 2:
```shell
awx job stdout 2
```

### job_template
* Run job:
```shell
$ awx job_template modify foo --extra_vars guid=1234 -f human --monitor
id  name
=== ==========
122 foo
```

* Modify job:
```shell
awx  job_template modify foo --extra_vars @./vars/my-config.yml
```

### config
```shell
awx config
```

```yaml
TOWER_COLOR: color
TOWER_FORMAT: format
TOWER_HOST: host
TOWER_PASSWORD: password
TOWER_USERNAME: username
TOWER_VERIFY_SSL: verify_ssl
TOWER_VERBOSE: verbose
TOWER_DESCRIPTION_ON: description_on
TOWER_CERTIFICATE: certificate
```

```
color 	        Boolean/’true’ 	        Whether to use colored output for highlighting or not.
formaat 	    String with options (‘human’, ‘json’, ‘yaml’)/’human’ 	Output format. The “human” format is intended for humans reading output on the CLI; the “json” and “yaml” formats provide more data.
host 	        String/‘127.0.0.1 ‘     The location of the Ansible Tower host. HTTPS is assumed as the protocol unless “http://” is explicitly provided.
password 	    String/’‘ 	            Password to use to authenticate to Ansible Tower.
username 	    String/’‘ 	            Username to use to authenticate to Ansible Tower.
verify_ssl 	    Boolean/’true’ 	        Whether to force verified SSL connections.
verbose 	    Boolean/’false’ 	    Whether to show information about requests being made.
description_on 	Boolean/’false’ 	    Whether to show description in human-formatted output.
certificate 	String/’‘ 	            Path to a custom certificate file that will be used throughout the command. Ignored if --insecure flag if set in command or verify_ssl is set to false
use_token 	    Boolean/’false’ 	    Whether to use token-based authentication.
```

## API
### References
* [API references](https://docs.ansible.com/ansible-tower/latest/html/towerapi/api_ref.html)

Example: https://awx.gigix/api/v2/users/

### curl
* With login / password:
```shell
curl -s -X GET --user ${TOWER_USERNAME}:${TOWER_PASSWORD} -k https://awx.gigix/api/v2/job_templates/  | jq .
```

* With token:
```shell
curl -X GET -H "Authorization: Bearer ${TOWER_OAUTH_TOKEN}" -k https://awx.gigix/api/v2/users/  | jq .
```

### Ansible
* With credentials:
```shell
---
- name: Tower API
  hosts: localhost
  become: false
  vars:
      tower_user: admin
      tower_pass: myadminpassword
      tower_host: 127.0.0.1
      tower_job_id: 7
    tasks:
  - name: Launch a new Job
    uri:
      url: https://{{ tower_host }}/api/v2/job_templates/{{ tower_job_id }}/launch/
      method: POST
      validate_certs: no
      return_content: yes
      user: "{{ tower_user }}"
      password: "{{ tower_pass }}"
      force_basic_auth: yes
      status_code: 201
```

* With token:
```shell
--
- name: Tower API

  hosts: localhost
  gather_facts: false

  vars:
    tower_user: admin
    tower_pass: myadminpassword
    tower_host: awx.gigix
    template_name: DEV template

  tasks:
    - name: Get the token
      uri:
        url: "https://{{ tower_host }}/api/v2/users/1/personal_tokens/"
        method: POST
        validate_certs: false
        return_content: true
        user: "{{ tower_user }}"
        password: "{{ tower_pass }}"
        force_basic_auth: true
        status_code: 201
      register: response

    - name: Use the token
      uri:
        url: "https://{{ tower_host }}/api/v2/job_templates/{{ template_name | urlencode }}/launch/"
        method: POST
        validate_certs: false
        return_content: true
        status_code: 201
        headers:
          Authorization: "Bearer {{ response['json']['token'] }}"
          Content-Type: "application/json"
      register: launch
```

### awxkit
```py
#!/usr/bin/env python3
import os, sys
from awxkit import api, config, utils
from awxkit.awx.utils import uses_sessions
from awxkit.exceptions import Unauthorized

config.assume_untrusted = True
config.client_connection_attempts = 1

#config.credentials = utils.PseudoNamespace({'default': {'username': 'admin', 'password': '2mlmp8'}})

config.base_url = os.getenv('TOWER_HOST', 'https://awx.gigix')
config.token = os.getenv('TOWER_OAUTH_TOKEN', None)
config.credentials = utils.PseudoNamespace({
    'default': {
        'username': os.getenv('TOWER_USERNAME', 'admin'),
        'password': os.getenv('TOWER_PASSWORD', 'password')
    }
})

root = api.Api()
root.load_session().get()
api_v2 = root.available_versions.v2.get()

if config.token:
    root.connection.login(
        None, None, token=config.token, auth_type='Bearer'
    )
else:
# if uses_sessions(root.connection):
    config.use_sessions = True
    root.load_session().get()

try:
    api_v2.me.get()
except Unauthorized as e:
    print(e.status_string)
    sys.exit(1)
except Exception as e:
    print(e)
    sys.exit(1)


# dir(api_v2) == the members of the object are all the top-level /api/v2/ endpoints
# these have python methods `get`, `put`, `patch` etc.
# e.g.
print(api_v2.hosts.get())
print(api_v2.ping.get())
```
