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

describe file('/home/genomicsdb/repos/TileDB') do
  it { should be_directory }
end

describe file('/home/genomicsdb/repos/TileDB/tiledb_cmd/bin/release/tiledb_load_csv') do
  it { should be_file }
end

describe file('/home/genomicsdb/repos/htslib') do
  it { should be_directory }
end

describe file('/home/genomicsdb/repos/rapidjson') do
  it { should be_directory }
end

describe file('/home/genomicsdb/DB') do
  it { should be_directory }
end

describe command('sudo -u ga4gh_writer -i psql -l | grep mappingdb | wc -l') do
  its(:stdout) { should match /1/}
end

describe command('sudo -u ga4gh_writer -i psql -c "\dt+" -d mappingdb | grep table | wc -l') do
  its(:stdout) { should match /15/}
end

describe user('ga4gh_writer') do
  it { should exist }
  it { should belong_to_group 'ga4gh' }
end

describe user('ga4gh_client') do
  it { should exist }
  it { should belong_to_group 'ga4gh' }
end

