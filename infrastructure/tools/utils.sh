#!/usr/bin/env bash

TMPDIR=/tmp/${USER}

#------------------------------------------------------------------------------
# If Travis, use /usr/bin/python
#------------------------------------------------------------------------------
if [[ -n "${TRAVIS}" ]]
then
    export PATH=/usr/bin:${PATH}
fi

#=== FUNCTION =================================================================
# NAME: cat_ansible_hosts
# DESCRIPTION: Create ephemeral inventory
#==============================================================================
function cat_ansible_hosts {
    mkdir ${TMPDIR} 2>/dev/null || true
    cat > ${TMPDIR}/hosts <<-EOF
	[all]
	127.0.0.1
	
	[all:vars]
	environment=development
	EOF
}

#=== FUNCTION =================================================================
# NAME: cat_ansible_site_yml
# DESCRIPTION: Create ephemeral playbook
#==============================================================================
function cat_ansible_site_yml {
    mkdir ${TMPDIR} 2>/dev/null || true
    cat > ${TMPDIR}/site.yml <<-EOF
	---
	- environment: "{{ env }}"
	  hosts: all
	  name: site
	  roles:
	$( if [ ${#*} -gt 0 ]
	   then
	       for role in ${@}
	       do
	           echo "    - ${role}"
	       done
	   else
	       echo   '    - "{{ role }}"'
	   fi
	 )
	  vars:
	    env:
	      GITHUB_TOKEN : "{{ lookup('env', 'GITHUB_TOKEN') }}"
	EOF
}

#=== FUNCTION =================================================================
# NAME: git_diff_files
# DESCRIPTION: List files that have diverged from the upstream merge base
#==============================================================================
function git_diff_files {
    if  [[ -n "${TRAVIS}" ]]
    then
        if [[ "${TRAVIS_PULL_REQUEST}" == "false" ]]
        then
            git fetch -q origin master:origin/master
            TRAVIS_COMMIT_RANGE="$( git merge-base FETCH_HEAD ${TRAVIS_BRANCH} )...${TRAVIS_COMMIT}"
        fi
        git --no-pager diff --name-only ${TRAVIS_COMMIT_RANGE}
    else
        git --no-pager diff --name-only @{u} HEAD
    fi
}

#=== FUNCTION =================================================================
# NAME: git_diff_playbooks
# DESCRIPTION: List playbooks that have been modified in git changeset
#==============================================================================
function git_diff_playbooks {
    #--------------------------------------------------------------------------
    # Explicitly set roles take precedence over explicitly set playbooks
    #--------------------------------------------------------------------------
    if [[ -n "${ROLE}" ]] \
    || [[ -n "${ROLES}" ]]
    then
        return
    fi
    #--------------------------------------------------------------------------
    # Explicitly set playbooks take precedence over modified files
    #--------------------------------------------------------------------------
    if [[ -n "${PLAYBOOK}" ]]
    then
        echo "${PLAYBOOK}" \
      | awk -F/ '/ansible\/[^/]+\.yml/ {
            gsub(/\.yml/, "", $2);
            print $2
        }'
    #--------------------------------------------------------------------------
    # Filter pertinent substring from list of divergent files
    #--------------------------------------------------------------------------
    else
        git_diff_files  \
      | awk -F/ '/ansible\/[^/]+\.yml/ {
            gsub(/\.yml/, "", $2);
            print $2
        }' \
      | sort -u
    fi
}

#=== FUNCTION =================================================================
# NAME: git_diff_roles
# DESCRIPTION: List roles that have been modified in git changeset
#==============================================================================
function git_diff_roles {
    #--------------------------------------------------------------------------
    # Explicitly set role takes precedence over explicitly set roles
    #--------------------------------------------------------------------------
    if   [[ -n "${ROLE}" ]]
    then
        echo "${ROLE}"
    #--------------------------------------------------------------------------
    # Explicitly set roles take precedence over modified files
    #--------------------------------------------------------------------------
    elif [[ -n "${ROLES}" ]]
    then
        for ROLE in $( echo ${ROLES//,/ } )
        do
            echo "${ROLE}"
        done
    #--------------------------------------------------------------------------
    # Filter pertinent substring from list of divergent files
    #--------------------------------------------------------------------------
    else
        git_diff_files \
      | awk -F/ '/ansible\/roles/ {
            print $3
        }' \
      | sort -u
    fi
}

#=== FUNCTION =================================================================
# NAME: get_roles_of_playbook
# DESCRIPTION: List roles that are affected by modified playbook(s)
#==============================================================================
function get_roles_of_playbook() {
    local playbook

    playbook=${1}

    python - <<-EOF
	from os.path import isfile
	from yaml import load
	
	yaml = 'ansible/${playbook}.yml'
	if isfile(yaml):
	    print '\n'.join([r for i in load(open(yaml))
	                     for r in i.get('roles', [])])
	EOF
}

#=== FUNCTION =================================================================
# NAME: get_dependents_of_role
# DESCRIPTION: List roles that are affected by modified roles(s)
#==============================================================================
function get_dependents_of_role() {
    local role

    role=${1}

    echo ${role}
    python - <<-EOF
	from glob import glob
	from yaml import load
	
	yamls = glob('ansible/roles/*/meta/main.yml')
	for yaml in yamls:
	    meta = load(open(yaml))
	    if meta is not None:
	        dependencies = meta.get('dependencies', [])
	        if '${role}' in [i.get('role') for i in dependencies]:
	            print yaml.split('/', 3)[2]
	EOF
}

#=== FUNCTION =================================================================
# NAME: get_recursive_dependencies_of_role
# DESCRIPTION: Get list of role and its recursive dependencies
#==============================================================================
function get_recursive_dependencies_of_role {
    local role

    role="${1}"

    python - <<-EOF
	from os import path
	from yaml import load
	
	def get_roles(role, roles=None):
	    if roles is None:
	        roles=set()
	    roles.add(role)
	    meta = 'ansible/roles/' + role + '/meta/main.yml'
	    if path.isfile(meta):
	        with open(meta) as yaml:
	            data = load(yaml)
	            if data is not None:
	                for dependency in data.get('dependencies', []):
	                    role = dependency.get('role')
	                    when = dependency.get('when')
	                    if (not when and
	                        role not in list(roles) + ['docker', 'docker-engine']):
	                        roles.add(role)
	                        get_roles(role, roles)
	    return roles
	
	for role in sorted(get_roles('${role}')):
	    print role
	EOF
}

#=== FUNCTION =================================================================
# NAME: get_random_sample_of_roles
# DESCRIPTION: List all roles
#==============================================================================
function get_random_sample_of_roles {
    cat /tmp/sample.txt 2>/dev/null \
 || ls ansible/roles/*/tasks/main.yml \
  | cut -d/ -f3 \
  | sort -R \
  | tail -n 10 \
  | tee /tmp/sample.txt
}

#=== FUNCTION =================================================================
# NAME: get_roles_to_install
# DESCRIPTION: List roles that have been modified in git changeset
#==============================================================================
function get_roles_to_install {
    local role

    #--------------------------------------------------------------------------
    # If Travis and branch is master, test roles that have diverged from
    # upstream merge-base and their first order dependents
    #--------------------------------------------------------------------------
    if [[ -n "${TRAVIS}" ]] \
    && [[    "${TRAVIS_BRANCH}" == "master" ]]
    then
        roles=(
              $( for role in $( git_diff_playbooks )
                 do
                     get_roles_of_playbook ${role}
                 done \
               | sort -u
               )
        )
        roles=(
              $( for role in ${roles[*]} $( git_diff_roles )
                 do
                     get_dependents_of_role ${role}
                 done \
               | sort -u
               )
        )
    #--------------------------------------------------------------------------
    # Otherwise test roles that have diverged from origin/master and their
    #--------------------------------------------------------------------------
    else
        roles=(
              $( git_diff_roles )
        )
    fi
    #--------------------------------------------------------------------------
    # If no roles have changed, default to testing all roles
    #--------------------------------------------------------------------------
    if [ ${#roles[@]} -eq 0 ]
    then
        roles=($( get_random_sample_of_roles ))
    fi
    export ROLES=$( printf -- "%s," ${roles[*]} )
    #--------------------------------------------------------------------------
    # Exclude galaxy roles
    #--------------------------------------------------------------------------
    roles=(
     $( comm -23 <( printf -- "%s\n" ${roles[*]} \
                  | egrep -v '\bopenvpn-client\b' \
                  | egrep -v '\bsudo\b' \
                  | sort
                  ) \
                 <( rev ansible_requirements.txt \
                  | cut -d/ -f1 \
                  | rev \
                  | sort
                  )
      )
    )
    #--------------------------------------------------------------------------
    # Skip roles that have been deleted
    #--------------------------------------------------------------------------
    for role in ${roles[@]}
    do
        if test -f ansible/roles/${role}/tasks/main.yml
        then
            echo ${role}
        fi
    done
}

#=== FUNCTION =================================================================
# NAME: get_roles_to_test
# DESCRIPTION: List roles that have been modified in git changeset
#==============================================================================
function get_roles_to_test {
    local role

    for role in $( get_roles_to_install )
    do
        get_recursive_dependencies_of_role ${role}
    done \
  | sort -u
}
