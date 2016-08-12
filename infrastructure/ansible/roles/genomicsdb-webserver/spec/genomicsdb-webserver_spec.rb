require 'spec_helper'

describe file('/home/genomicsdb/DB/test') do
  it { should be_directory }
end

describe file('/home/genomicsdb/repos/GenomicsSampleAPIs/web/ga4gh_test.ini') do
  it { should exist }
end

describe file('/home/genomicsdb/repos/GenomicsSampleAPIs/web/ga4gh_test.conf') do
  it { should exist }
end

describe file('/var/uwsgi/ga4gh_test.sock') do
  it { should exist }
  it { should be_socket }
end

describe file('/etc/init/ga4gh_test.conf') do
  it { should exist }
end

describe service('ga4gh_test') do
  it { should be_enabled }
  it { should be_running }
end

describe file('/etc/nginx/conf.d/nginx_ga4gh_test.conf') do
  it { should exist }
end

describe port(8990) do
  it { should be_listening }
end

describe command('curl -H "Content-Type: application/json" -X POST -d \'{"end": 27507000, "pageSize": 31, "start": 27506000, "pageToken": null, "variantSetIds": [], "variantName": null, "referenceName": "13"}\'  localhost:8990/variants/search | grep alternateBases | wc -l') do
  its(:stdout) { should match /2/}
end
