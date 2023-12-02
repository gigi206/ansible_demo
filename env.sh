#!/usr/bin/env bash
INSTALL_PATH="$(realpath $(dirname $0))"
source "${INSTALL_PATH}/env/bin/activate"
# export ANSIBLE_INVENTORY="${INSTALL_PATH}/hosts"
export ANSIBLE_VAULT_PASSWORD_FILE=$(realpath ./vault_password)
