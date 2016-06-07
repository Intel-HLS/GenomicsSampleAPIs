# Ansible Spec Documentation

### Description:
Ansible_Spec is a Ruby gem that implements an Ansible Config Parser for Serverspec. It creates a Rake task that can run tests, using Ansible inventory files and playbooks. You can test multiple roles and multiple hosts.

### Best practices for unit testing roles
Each role should be tested using the following conventions:
- Verify that the tool defined by the role has installed as expected
  - This might mean checking the existence of a file:

      ```ruby
        describe file('/etc/passwd') do
          it { should exist }
        end
      ```

  - Or confirming that a directory has been created:

      ```ruby
        describe file('/var/log/httpd') do
          it { should be_directory }
        end
      ```

  - Or verifying tool version if there is a hard dependency:

      ```ruby
        describe package('docopt') do
          it { should be_installed.by('pip').with_version('0.16') }
        end
      ```

  - Although many of these tests are accomplished during the initial provisioning process, providing explicit unit tests has two benefits:
    - 1. There may be different versions of the same tool installed through various roles. Without error checking within a task, this might not be caught at the time of provisioning.
    - 2. Makes CI much easier.

- Confirming tool functionality + Server configuration
  - Server ports may change depending on whether the provisioning process occurs on a baremetal cluster vs. a NUC (for example). Testing ports is essential in this scenario, and should be tested in a variety of ways. These may include:
    - Initially verifying the port number in the nginx configuration file:

    ```ruby
    describe file('/etc/nginx/conf.d/ssl.conf') do
      its(:content) { should match /listen       3000/ }
    end
    ```

    - Is the nginx server running?

    ```ruby
    describe service('nginx') do
      it { should be_running }
    end
    ```

    - Is it reachable on the specified port?

    ```ruby
    describe host('austin-gateway.ccc.org') do
      it { should be_reachable.with( :port => 3000 ) }
    end
    ```

### How to run unit tests
1. After your ROLENAME_spec.rb has been created, add ROLENAME to the ```CCC_Infrastructure/ansible/spec/role_names.txt``` file.
2. Run ```./bin/runspec.sh```

###More Ansible Spec Examples
If you would like more examples, see the full ServerSpec documentation [here](http://serverspec.org/resource_types.html)
