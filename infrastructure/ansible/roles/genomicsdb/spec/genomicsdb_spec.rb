require 'spec_helper'

describe file('/home/genomicsdb/repos/GenomicsSampleAPIs') do
  it { should be_directory }
end

describe file('/home/genomicsdb/repos/GenomicsSampleAPIs/search_library/lib/libquery.so') do
  it { should be_file }
end

describe file('/home/genomicsdb/repos/GenomicsSampleAPIs/web/templates') do
  it { should be_directory }
end

describe file('/home/genomicsdb/repos/GenomicsSampleAPIs/dependencies/GenomicsDB') do
  it { should be_directory }
end

describe file('/home/genomicsdb/repos/search_library/dependencies/GenomicsDB/dependencies/htslib') do
  it { should be_directory }
end

describe file('/home/genomicsdb/repos/search_library/dependencies/GenomicsDB/dependencies/rapidjson') do
  it { should be_directory }
end

describe file('/home/genomicsdb/DB') do
  it { should be_directory }
end

describe user('ga4gh_writer') do
  it { should exist }
  it { should belong_to_group 'ga4gh' }
end

describe user('ga4gh_client') do
  it { should exist }
  it { should belong_to_group 'ga4gh' }
end

describe command('sudo -u ga4gh_writer -i psql -l | grep metadb | wc -l') do
  its(:stdout) { should match /1/}
end

describe command('sudo -u ga4gh_writer -i psql -c "\dt+" -d metadb | grep table | wc -l') do
  its(:stdout) { should match /15/}
end
