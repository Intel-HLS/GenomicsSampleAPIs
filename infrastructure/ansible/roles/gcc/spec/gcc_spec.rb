require 'spec_helper'

describe command('/opt/rh/devtoolset-3/root/bin/gcc -dumpversion'), :if => os[:family] == 'redhat' do
  its(:stdout) { should match /4.9.3/ }
end

describe command('/usr/bin/gcc -dumpversion'), :if => os[:family] == 'ubuntu' do
  its(:stdout) { should match /4.9.3/ }
end

describe command('/opt/rh/devtoolset-3/root/bin/g++ -dumpversion'), :if => os[:family] == 'redhat' do
  its(:stdout) { should match /4.9.3/ }
end

describe command('/usr/bin/g++ -dumpversion'), :if => os[:family] == 'ubuntu' do
  its(:stdout) { should match /4.9.3/ }
end
