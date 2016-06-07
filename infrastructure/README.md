## Build indicators

| Branch         | Status           |
| :-------------: |:-------------:|
| [master](https://github.com/Intel-HSS/CCC_Infrastructure/tree/master)      | [![Build Status](https://travis-ci.com/Intel-HSS/CCC_Infrastructure.svg?token=WUxqYhsyxLCiKp7Dsi2e&branch=master)](https://travis-ci.com/Intel-HSS/CCC_Infrastructure) |
| [application-node-playbook](https://github.com/Intel-HSS/CCC_Infrastructure/tree/application-node-playbook)     | [![Build Status](https://travis-ci.com/Intel-HSS/CCC_Infrastructure.svg?token=WUxqYhsyxLCiKp7Dsi2e&branch=application-node-playbook)](https://travis-ci.com/Intel-HSS/CCC_Infrastructure)  |
| [compute-node-playbook](https://github.com/Intel-HSS/CCC_Infrastructure/tree/compute-node-playbook)     | [![Build Status](https://travis-ci.com/Intel-HSS/CCC_Infrastructure.svg?token=WUxqYhsyxLCiKp7Dsi2e&branch=compute-node-playbook)](https://travis-ci.com/Intel-HSS/CCC_Infrastructure)  |
| [gateway-node-playbook](https://github.com/Intel-HSS/CCC_Infrastructure/tree/gateway-node-playbook)     | [![Build Status](https://travis-ci.com/Intel-HSS/CCC_Infrastructure.svg?token=WUxqYhsyxLCiKp7Dsi2e&branch=gateway-node-playbook)](https://travis-ci.com/Intel-HSS/CCC_Infrastructure)      |

## Purpose for CCC Infrastructure

The infrastructure team is responsible for laying down the essential
components needed for reproducible, managable, and reliable systems.
Documentation, testing, and reusable code are important to maintain
integrity.

## Systems

There are three primary system types to consider for core infrastructure

* Central function
* Gateways
* Cluster nodes

## Operations

Each system type should be able to be:

* Spun up as a VM or bare metal
* Provisioned and re-provisioned through configuration management
* Monitored for status and health
