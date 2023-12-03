# AWX / TOWER
## Documentation
* [Tower](https://docs.ansible.com/ansible-tower/latest/html/)
* [Ansible](https://ansible.readthedocs.io/projects/awx/en/latest/)

## Change password
```shell
kubectl -n awx-operator exec -it deployments/awx-web -c awx-web -- awx-manage changepassword admin
Changing password for user 'admin'
Password:
Password (again):
Password changed successfully for user 'admin'
```
