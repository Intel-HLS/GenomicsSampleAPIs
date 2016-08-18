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

import sys
import os
import config
from ga4gh import create_app
from ga4gh import views

ga4ghPath = None
for path in sys.path:
    if path.endswith('web'):
        ga4ghPath = path
        break
if ga4ghPath is None:
    raise Exception("GA4GHAPI path is not set. Run GenomicsSampleAPIs/web/install.py, \
  and use --system-site-packages when creating a virtualenv")


config.initConfig(os.path.join(ga4ghPath, "ga4gh_test.conf"))

if os.getenv('VIRUTAL_ENV') is None:
    activate_this = config.LoadedConfig.VIRTUALENV + '/bin/activate_this.py'
    execfile(activate_this, dict(__file__=activate_this))

application = create_app('config.LoadedConfig')

application.register_blueprint(views.ga4gh)
