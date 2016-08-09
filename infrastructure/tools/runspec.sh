#!/usr/bin/env bash

set -e

pwd=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
. ${pwd}/utils.sh

roles=( $( get_roles_to_test ) )

TMPDIR=/tmp/${USER}

cd ansible

if [ ${#roles[*]} -gt 0 ]
then
    export PLAYBOOK=${TMPDIR}/site.yml
    cat_ansible_site_yml ${roles[*]}
fi

if [ -n "${CONTINUOUS_INTEGRATION}" ]
then
    export INVENTORY=${TMPDIR}/hosts
    cat_ansible_hosts
    sudo -E su -c "source ${rvm_path}/scripts/rvm; rake serverspec:site"
else
    export INVENTORY=../.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory
    # Add extra parameters to Ansible inventory for serverspec to function
    params+='ansible_ssh_user=vagrant '
    params+='ansible_become=yes '
    params+='ansible_become_user=root '
    sed -i -e "/ansible_become/!s/\(.*ansible_ssh.*\)/\1 ${params}/" ${INVENTORY}
    # Append parameters to host declarations within groups for serverspec to function
    hosts=( $( awk '/ansible_ssh/ {print $1}' ${INVENTORY} ) )
    for host in ${hosts[@]}
    do
        params=$( awk "/${host} / {for (i = 2; i <= NF; i++) printf(\"%s \", \$i)}" ${INVENTORY} )
        sed -i -e "s#^${host}\$#${host} ${params}#" ${INVENTORY}
    done
    rake serverspec:site
fi

cd -
exit 0
