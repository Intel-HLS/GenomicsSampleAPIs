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

