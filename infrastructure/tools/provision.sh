#!/usr/bin/env bash

set -e

pwd=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
. ${pwd}/utils.sh

roles=( $( get_roles_to_install ) )

TMPDIR=/tmp/${USER}

if [ -n "${CONTINUOUS_INTEGRATION}" ]
then
    export PLAYBOOK=${TMPDIR}/site.yml
    for role in ${roles[@]}
    do
        cat_ansible_site_yml ${role}

        #----------------------------------------------------------------------
        # Create symlinks to directories required by playbook
        #----------------------------------------------------------------------
        dirs=(
         $( find ansible -maxdepth 1 -mindepth 1 -type d \
          | xargs -l1 basename
          )
        )
        for dir in ${dirs[@]}
        do
            ln -s ${pwd}/../ansible/${dir} ${TMPDIR}/${dir} 2>/dev/null || true
        done
        #----------------------------------------------------------------------
        # TODO(khrisric): should iterate over modified playbooks too
        # TODO(khrisric): preferrable to test roles in isolated VMs
        # TODO(khrisric): reuse trigger_build.sh to test roles in separate VMs?
        #----------------------------------------------------------------------
        if [[ "${role}" == "zookeeper-server" ]]
        then
            sudo apt-get -y remove zookeeper
        fi

        ansible-playbook -i "localhost," ${PLAYBOOK} \
            --connection=local \
            --syntax-check
        ansible-playbook -i "localhost," ${PLAYBOOK} \
            --connection=local \
            --extra-vars="pkg_manager_proxy_config_file=./test_cfg_proxy" \
            --sudo
    done
else
    #--------------------------------------------------------------------------
    # TODO(khrisric): should iterate over modified playbooks too
    #--------------------------------------------------------------------------
    export ROLES=$( printf -- "%s," ${roles[*]} )
    vagrant up
    vagrant provision --provision-with ansible
    #--------------------------------------------------------------------------
    # In the default Vagrant environment (i.e. - no playbooks or roles being
    # tested explicitly), use Ansible to provision the application and compute
    # nodes from the gateway
    #--------------------------------------------------------------------------
    if [ ${#roles[*]} -eq 0 ]
    then
        INVENTORY=/vagrant/.vagrant/provisioners/ansible/inventory/hosts
        PLAYBOOK=/vagrant/ansible/site.yml
        if vagrant status | egrep -q 'g0\s+running'
        then
            vagrant ssh g0 -- \
                ANSIBLE_HOST_KEY_CHECKING=False \
                ansible-playbook  -e "phase=2" -i ${INVENTORY} ${PLAYBOOK}
        fi
    fi
fi

exit 0
