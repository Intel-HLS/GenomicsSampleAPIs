#!/usr/bin/env bash

for vm in $( VBoxManage list vms 2>/dev/null \
           | cut -d{ -f2 \
           | cut -d} -f1
           )
do
    VBoxManage controlvm    ${vm} poweroff
    VBoxManage unregistervm ${vm} --delete
done
