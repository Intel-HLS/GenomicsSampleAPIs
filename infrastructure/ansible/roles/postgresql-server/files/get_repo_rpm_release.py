"""
  The MIT License (MIT)
  Copyright (c) 2016 Intel Corporation

  Permission is hereby granted, free of charge, to any person obtaining a copy of 
  this software and associated documentation files (the "Software"), to deal in 
  the Software without restriction, including without limitation the rights to 
  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of 
  the Software, and to permit persons to whom the Software is furnished to do so, 
  subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all 
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

#!/usr/bin/env python
"""
Determine the latest version of the yum repository package.

usage: get_repo_rpm_version.py url distribution

e.g.:

get_repo_rpm_version.py http://yum.postgresql.org/9.2/redhat/rhel-6-x86_64/ centos
"""

import re
import sys
import urllib2

url, dist = sys.argv[1:]

try:
    repo = urllib2.urlopen(url)
except urllib2.HTTPError as e:
    print >>sys.stderr, "Failed to fetch directory list from %s" % url
    raise

pg_version = url.split('/')[3]
if pg_version[0] == "8" and dist != "sl":
    re_pattern = 'href=[\'"](pgdg-%s-%s-[\d+].noarch.rpm)[\'"]' % (dist, pg_version)
else:
    re_pattern = 'href=[\'"](pgdg-%s%s-%s-[\d+].noarch.rpm)[\'"]' % (dist,
                                                                     pg_version.replace('.', ''), pg_version)
match = re.findall(re_pattern, repo.read(), flags=re.I)

assert match, "No matching %s pgdg repository packages found for version %s at %s" % (
    dist, pg_version, url)

print match[0]

sys.exit(0)
