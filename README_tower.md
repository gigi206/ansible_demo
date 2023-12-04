# AWX / TOWER
## Documentation
* [Tower](https://docs.ansible.com/ansible-tower/latest/html/)
* [Ansible](https://ansible.readthedocs.io/projects/awx/en/latest/)

## Tuto
### Change admin password
```shell
kubectl -n awx-operator exec -it deployments/awx-web -c awx-web -- awx-manage changepassword admin
Changing password for user 'admin'
Password:
Password (again):
Password changed successfully for user 'admin'
```

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
export TOWER_OAUTH_TOKEN=nBuUAFRfhjSHQxClRgrK6Hmi7UG8gS
```

See also variable `TOWER_USERNAME` and `TOWER_PASSWORD`.

### config
```shell
awx config
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
