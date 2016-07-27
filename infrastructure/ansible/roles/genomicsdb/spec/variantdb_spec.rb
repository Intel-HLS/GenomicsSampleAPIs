require 'spec_helper'

describe file('/home/variantdb/repos/GenomicsSampleAPIs') do
  it { should be_directory }
end

describe file('/home/variantdb/repos/GenomicsSampleAPIs/search_library/lib/libquery.so') do
  it { should be_file }
end

describe file('/home/variantdb/repos/GenomicsSampleAPIs/web/templates') do
  it { should be_directory }
end

describe file('/home/variantdb/repos/TileDB') do
  it { should be_directory }
end

describe file('/home/variantdb/repos/TileDB/tiledb_cmd/bin/release/tiledb_load_csv') do
  it { should be_file }
end

describe file('/home/variantdb/repos/htslib') do
  it { should be_directory }
end

describe file('/home/variantdb/repos/rapidjson') do
  it { should be_directory }
end

describe file('/home/variantdb/DB') do
  it { should be_directory }
end

describe command('sudo -u ga4gh_writer -i psql -l | grep metadb | wc -l') do
  its(:stdout) { should match /1/}
end

describe command('sudo -u ga4gh_writer -i psql -c "\dt+" -d metadb | grep table | wc -l') do
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

