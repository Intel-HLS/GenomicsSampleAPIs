# vi: set ft=ruby :

require 'spec_helper'

debian = ['debian', 'ubuntu']
redhat = ['redhat']

if debian.include?(os[:family])

  describe package('postgresql') do
    it { should be_installed }
  end

  describe service('postgresql') do
    it { should be_enabled }
    it { should be_running }
  end

  describe file('/etc/postgresql/9.4/main/postgresql.conf') do
    it { should be_file }
  end

elsif redhat.include?(os[:family])

  describe package('postgresql94-server') do
    it { should be_installed }
  end

  describe service('postgresql-9.4') do
    it { should be_enabled }
    it { should be_running }
  end

  describe file('/var/lib/pgsql/9.4/data/postgresql.conf') do
    it { should be_file }
  end

end

describe port(5432) do
  it { should be_listening.with('tcp') }
end
