# AWX / TOWER
## Documentation
* https://docs.ansible.com/ansible-tower/latest/html/

## Change password
```shell
kubectl -n awx-operator exec -it deployments/awx-web -c awx-web -- awx-manage changepassword admin
Changing password for user 'admin'
Password:
Password (again):
Password changed successfully for user 'admin'
```
